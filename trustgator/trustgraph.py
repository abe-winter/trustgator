"trustgraph.py -- getters, setters and enumerators over the 2-hop graph"
import flask, collections
from datetime import datetime
from . import util, auth

# rate limit per user (use DB, make this one configurable)
@util.STATS.timer('func.submit_link')
def submit_link(form: dict):
  assert len(form['title']) < 400
  assert len(form['url']) < 4000
  userid = flask.g.sesh['userid']
  if not auth.submit_allowed():
    return 'Sorry -- this server has gate_submits on, which means you need to get one vouch to submit links (or be an admin)'
  ret = flask.current_app.queries.insert_link(
    userid=userid,
    title=form['title'],
    url=form['url']
  )
  util.clear_cache('load_pubuser', userid)
  return flask.redirect(flask.url_for('get_link', linkid=ret['linkid']))

# todo: crank up ttl_secs when system is busy
@util.cache_wrapper('load_article', ttl_secs=util.CONF['redis_ttl'])
@util.STATS.timer('func.load_article')
def load_article(linkid: str):
  "load link and related resources"
  queries = flask.current_app.queries
  link = queries.load_link(linkid=linkid)
  if not link:
    flask.abort(404)
  asserts = list(queries.load_link_asserts(linkid=linkid))
  vouches = queries.load_vouch_counts(assertids=[assert_['assertid'] for assert_ in asserts])
  vouch_dict = collections.defaultdict(dict)
  for vouch in vouches:
    vouch_dict[vouch['assertid']][vouch['score']] = vouch['count']
  now = datetime.utcnow()
  for assert_ in asserts:
    assert_['vouches'] = sorted(vouch_dict.get(assert_['assertid'], {}).items())
    assert_['deletable'] = (now - assert_['created']).total_seconds() < 60 * util.CONF['delete_minutes']['assert']
  flag_count = queries.link_flag_count(linkid=linkid)['count']
  return {'link': link, 'asserts': asserts, 'age_seconds': (now - link['created']).total_seconds(), 'flag_count': flag_count}

@util.cache_wrapper('load_overlay', ttl_secs=1) # todo: long_ttl
@util.Degrader('trustnet', {'error': "Load is too darn high! Skipping this"})
def load_overlay(linkid: str):
  "load asserts in graph context"
  queries = flask.current_app.queries
  link = queries.load_link(linkid=linkid)
  if not link:
    flask.abort(404)
  # for users asserting on this article, get your vouch history x their topics
  # also pull 2nd-degree
  userid = flask.g.sesh['userid']
  return {
    'link': link,
    'hop1': queries.link_overlay_1hop(linkid=linkid, userid=userid),
    'hop2': queries.link_overlay_2hop(linkid=linkid, userid=userid),
  }

def submit_assert(form: dict):
  assert form['linkid']
  assert len(form['topic']) < 128
  assert len(form['body']) < 2000
  userid = flask.g.sesh['userid']
  flask.current_app.queries.insert_assert(
    userid=userid,
    linkid=form['linkid'],
    topic=form['topic'],
    claim=form['body'],
  )
  util.clear_cache('load_article', form['linkid'])
  util.clear_cache('load_pubuser', userid)
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
  userid = flask.g.sesh['userid']
  flask.current_app.queries.insert_vouch(
    userid=userid,
    assertid=form['assertid'],
    score=score,
  )
  # todo: cache invalidation is a tough accounting problem; automate or lint
  # note: only clear cache after the DB has validated the vouch above
  util.clear_cache('load_assertion', form['assertid'])
  util.clear_cache('load_pubuser', userid)
  return flask.redirect(flask.url_for('get_assert', assertid=form['assertid']))

# todo: think about how to mix cache_wrapper and degrader; I don't want to include cache hit times in the degrader computation *but* I also don't want to cache timing errors (or do I)
@util.cache_wrapper('global_articles', ttl_secs=util.CONF['redis_ttl'])
@util.Degrader('global', {'items': [], 'error': "Load is too darn high! Skipping this"})
def global_articles():
  # note: this cache doesn't get cleared; this can be eventually consistent for perf reasons
  return {
    'items': list(flask.current_app.queries.load_global_active(wide_count=100, narrow_count=20)),
    'error': None,
  }

@util.cache_wrapper('articles_1hop', ttl_secs=util.CONF['redis_long_ttl'])
@util.Degrader('2hop', {'items': [], 'error': "Load is too darn high! Skipping this"})
def articles_1hop(userid):
  return {
    'items': list(flask.current_app.queries.links_1hop(userid=userid, limit=5)),
    'error': None,
  }

@util.cache_wrapper('articles_2hop', ttl_secs=util.CONF['redis_long_ttl'])
@util.Degrader('2hop', {'items': [], 'error': "Load is too darn high! Skipping this"})
def articles_2hop(userid):
  return {
    'items': list(flask.current_app.queries.links_2hop(userid=userid, limit=5)),
    'error': None,
  }

@util.cache_wrapper('articles_vouchers', ttl_secs=util.CONF['redis_long_ttl'])
@util.Degrader('2hop', {'items': [], 'error': "Load is too darn high! Skipping this"})
def articles_vouchers(userid):
  return {
    'items': list(flask.current_app.queries.links_vouchers(userid=userid, limit=5)),
    'error': None,
  }

@util.cache_wrapper('load_pubuser', ttl_secs=util.CONF['redis_long_ttl'])
@util.Degrader('pubuser', {'error': "Load is too darn high! Skipping this"})
def load_pubuser(userid: str):
  queries = flask.current_app.queries
  user = queries.get_pubuser(userid=userid)
  if not user or user['delete_on']:
    return {'error': 'User missing or deletd'}
  return {
    'user': user,
    'links': list(queries.get_user_links(userid=userid, limit=100)),
    'asserts': list(queries.get_user_asserts(userid=userid, limit=100)),
    'vouches': list(queries.get_user_vouches(userid=userid, limit=100)),
    'error': None,
  }

@util.cache_wrapper('load_trustnet', ttl_secs=util.CONF['redis_long_ttl'])
@util.Degrader('trustnet', {'error': "Load is too darn high! Skipping this"})
def load_trustnet(userid: str):
  queries = flask.current_app.queries
  return {
    'hop1': list(queries.load_user_vouchees(userid=userid, limit=100)),
    'hop2': list(queries.load_user_vouchees_2(userid=userid, limit=100)),
    'incoming': list(queries.load_user_vouchers(userid=userid, limit=100)),
    'error': None,
  }

def delete_link(form: dict):
  assert form['linkid']
  link = flask.current_app.queries.load_link(linkid=form['linkid'])
  if not link:
    flask.abort(404)
  if str(link['userid']) != flask.g.sesh['userid']:
    flask.abort(403)
  if (datetime.utcnow() - link['created']).total_seconds() > util.CONF['delete_minutes']['link'] * 60:
    return 'too late to delete this'
  flask.current_app.queries.del_link(linkid=form['linkid'])
  util.clear_cache('load_article', form['linkid'])
  util.clear_cache('load_pubuser', flask.g.sesh['userid'])
  return flask.redirect(flask.url_for('get_home'))

def delete_assert(form: dict):
  assert form['assertid']
  assert_ = flask.current_app.queries.get_assert(assertid=form['assertid'])
  if not assert_:
    flask.abort(404)
  if str(assert_['userid']) != flask.g.sesh['userid']:
    flask.abort(403)
  if (datetime.utcnow() - assert_['created']).total_seconds() > util.CONF['delete_minutes']['assert'] * 60:
    return 'too late to delete this'
  flask.current_app.queries.del_assert(assertid=form['assertid'])
  util.clear_cache('load_article', str(assert_['linkid']))
  util.clear_cache('load_assertion', form['assertid'])
  util.clear_cache('load_pubuser', flask.g.sesh['userid'])
  return flask.redirect(flask.url_for('get_link', linkid=assert_['linkid']))

def flag_link(linkid: str, form: dict):
  assert form['category'] in ('law', 'policy')
  assert form['which'] and len(form['which']) < 1000
  if not auth.submit_allowed():
    flask.abort(403)
  flask.current_app.queries.flag_link(
    linkid=linkid,
    userid=flask.g.sesh['userid'],
    category=form['category'],
    detail=form['which']
  )
  return flask.redirect(flask.url_for('get_link', linkid=linkid))
