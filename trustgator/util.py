import statsd, varyaml, os
from datetime import datetime

CONF = varyaml.load(open(os.environ.get('VARYAML', 'varyaml.yml')))

STATS = statsd.StatsClient(prefix='tgtr.')

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
