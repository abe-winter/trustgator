"trustgraph.py -- getters, setters and enumerators over the 2-hop graph"
import flask, collections
from . import util

# stats timing and reject writes when system is busy
# rate limit per user (use DB, make this one configurable)
def submit_link(form: dict):
  assert len(form['title']) < 400
  assert len(form['url']) < 4000
  ret = flask.current_app.queries.insert_link(
    userid=flask.g.sesh['userid'],
    title=form['title'],
    url=form['url']
  )
  return flask.redirect(flask.url_for('get_link', linkid=ret['linkid']))

# todo: crank up ttl_secs when system is busy
@util.cache_wrapper('load_article', ttl_secs=util.CONF['redis_ttl'])
# todo: stats timing here
def load_article(linkid: str):
  "load link and related resources"
  link = flask.current_app.queries.load_link(linkid=linkid)
  if not link:
    flask.abort(404)
  asserts = list(flask.current_app.queries.load_link_asserts(linkid=linkid))
  vouches = flask.current_app.queries.load_vouch_counts(assertids=[assert_['assertid'] for assert_ in asserts])
  vouch_dict = collections.defaultdict(dict)
  for vouch in vouches:
    vouch_dict[vouch['assertid']][vouch['score']] = vouch['count']
  for assert_ in asserts:
    assert_['vouches'] = sorted(vouch_dict.get(assert_['assertid'], {}).items())
  return {'link': link, 'asserts': asserts}

def submit_assert(form: dict):
  assert form['linkid']
  assert len(form['topic']) < 128
  assert len(form['body']) < 2000
  flask.current_app.queries.insert_assert(
    userid=flask.g.sesh['userid'],
    linkid=form['linkid'],
    topic=form['topic'],
    claim=form['body'],
  )
  util.clear_cache('load_article', form['linkid'])
  return flask.redirect(flask.url_for('get_link', linkid=form['linkid']))

@util.cache_wrapper('load_assertion', ttl_secs=util.CONF['redis_ttl'])
def load_assertion(assertid: str):
  assert_ = flask.current_app.queries.load_join_assert(assertid=assertid)
  vouches = list(flask.current_app.queries.load_assert_vouches(assertid=assertid))
  vouch_counts = list(collections.Counter(vouch['score'] for vouch in vouches).items())
  return assert_, vouches, vouch_counts

def submit_vouch(form: dict):
  assert form['assertid']
  score = int(form['score'])
  assert score >= -2 and score <= 2
  # note: *not* doing a foreign key check of assertid; at worst we have a bunch of random uuids in there attached to bad users
  flask.current_app.queries.insert_vouch(
    userid=flask.g.sesh['userid'],
    assertid=form['assertid'],
    score=score,
  )
  # todo: cache invalidation is a tough accounting problem; automate or lint
  # note: only clear cache after the DB has validated the vouch above
  util.clear_cache('load_assertion', form['assertid'])
  return flask.redirect(flask.url_for('get_assert', assertid=form['assertid']))

@util.cache_wrapper('global_articles', ttl_secs=util.CONF['redis_ttl'])
def global_articles():
  # note: this cache doesn't get cleared; this can be eventually consistent for perf reasons
  return list(flask.current_app.queries.load_global_active(wide_count=100, narrow_count=10))

@util.cache_wrapper('articles_1hop', ttl_secs=util.CONF['redis_long_ttl'])
def articles_1hop(userid):
  return list(flask.current_app.queries.links_1hop(
    userid=userid,
    limit=5,
  ))

@util.cache_wrapper('articles_2hop', ttl_secs=util.CONF['redis_long_ttl'])
def articles_2hop(userid):
  return list(flask.current_app.queries.links_2hop(
    userid=userid,
    limit=5,
  ))
