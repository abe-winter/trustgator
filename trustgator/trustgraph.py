"trustgraphy.py -- getters, setters and enumerators over the 2-hop graph"
import flask, collections
from . import util

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
@util.cache_wrapper('load_article', ttl_secs=5)
def load_article(linkid: str):
  "load link and related resources"
  link = flask.current_app.queries.load_link(linkid=linkid)
  if not link:
    flask.abort(404)
  asserts = flask.current_app.queries.load_link_asserts(linkid=linkid)
  vouches = flask.current_app.queries.load_vouch_counts(assertids=[assert_['assertid'] for assert_ in asserts])
  vouch_dict = collections.defaultdict(dict)
  for vouch in vouches:
    vouch_dict[vouch['assertid']][vouch['score']] = vouch['count']
  for assert_ in asserts:
    assert_['vouches'] = vouch_dict.get(assert_['assertid']) or {}
  return {
    'link': link,
    'asserts': asserts,
  }
