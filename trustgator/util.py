import statsd, varyaml, os, flask, functools, flask, rapidjson, collections, logging, time
from datetime import datetime

CONF = varyaml.load(open(os.environ.get('VARYAML', 'varyaml.yml')))

STATS = statsd.StatsClient(prefix='tgtr.', host=CONF['stats_host'])

def minute_floor(datetime_: datetime) -> datetime:
  return datetime(*datetime_.timetuple()[:5])

class RateLimiter:
  def __init__(self, name, max_per_minute):
    self.name = name
    self.base = None
    self.count = 0
    assert max_per_minute > 0
    self.max_per_minute = max_per_minute

  def check(self, now=None) -> bool:
    "returns bool where True means you're under limit"
    # todo: test with out-of-order timestamps; should under-limit
    now = now or datetime.utcnow()
    base = minute_floor(now)
    if self.base == base:
      if self.count >= self.max_per_minute:
        STATS.incr(f'ratelimit.{self.name}')
        return False
      self.count += 1
    else:
      self.base = base
      self.count = 1
    return True

UNIQUE_NAMES = []
DEFAULT_CACHEID = 'global'

def cache_wrapper(name: str, ttl_secs: int):
  "cache in redis"
  assert name not in UNIQUE_NAMES
  UNIQUE_NAMES.append(name)
  def wrapper(inner):
    @functools.wraps(inner)
    def outer(*args, **kwargs):
      cacheid = args[0] if args else DEFAULT_CACHEID
      if not flask.current_app: # is this some test suite case? booting up?
        return inner(*args, **kwargs)
      key = rapidjson.dumps({'name': name, 'id': cacheid}, sort_keys=True)
      probe = flask.current_app.redis_cache.get(key)
      if probe:
        STATS.incr(f'cwrap.{name}.hit')
        return rapidjson.loads(probe)
      STATS.incr(f'cwrap.{name}.miss')
      val = rapidjson.dumps(
        inner(*args, **kwargs),
        uuid_mode=rapidjson.UM_CANONICAL,
        datetime_mode=rapidjson.DM_ISO8601,
      )
      flask.current_app.redis_cache.set(key, val, ex=ttl_secs)
      return rapidjson.loads(val)
    return outer
  return wrapper

def clear_cache(name: str, cacheid=DEFAULT_CACHEID):
  key = rapidjson.dumps({'name': name, 'id': cacheid}, sort_keys=True)
  flask.current_app.redis_cache.delete(key)

TimePair = collections.namedtuple('TimePair', 'time value')

class Degrader:
  "decorator to return a dummy response when a route is taking too long (for shedding load)"
  def __init__(self, name, dummy, max_time=0.25, history=10, lookback_secs=30, stats=STATS):
    self.name = name
    self.dummy = dummy
    self.max_time = max_time
    assert history > 0
    self.history = history
    self.lookback_secs = lookback_secs
    self.times = collections.deque()
    self.stats = stats

  def trim(self, now):
    "remove old and over-limit elements from queue"
    while len(self.times) > self.history:
      self.times.popleft()
    while self.times and now - self.times[0].time > self.lookback_secs:
      self.times.popleft()

  def over_limit(self):
    return sum(pair.value for pair in self.times) > self.max_time

  def __call__(self, wrapped):
    "decorator"
    @functools.wraps(wrapped)
    def wrapper(*args, **kwargs):
      t0 = time.time()
      self.trim(t0)
      if self.over_limit():
        if self.stats: self.stats.incr(f'degrader.over.{self.name}', 1)
        return self.dummy
      if self.stats: self.stats.incr(f'degrader.under.{self.name}', 1)
      ret = wrapped(*args, **kwargs)
      now = time.time()
      self.times.append(TimePair(now, now - t0))
      return ret
    return wrapper
