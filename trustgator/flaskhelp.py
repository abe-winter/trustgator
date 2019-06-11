import logging, contextlib, flask, functools, pugsql, json, redis
from typing import Optional
from . import db
from .util import CONF

def setup_db():
  # todo: figure out pooling with pug
  queries = pugsql.module('./sql/queries')
  queries.connect(db.db_url())
  flask.current_app.queries = queries

def setup_redis():
  flask.current_app.redis_sessions = redis.StrictRedis(CONF['redis']['sessions'])
  flask.current_app.redis_cache = redis.StrictRedis(CONF['redis']['cache'])

def session_key(sessionid: str) -> str:
  return json.dumps({'sessionid': sessionid})

def get_session(redis, sessionid: str) -> Optional[str]:
  val = redis.get(session_key(sessionid))
  return json.loads(val) if val else None

def require_session(inner):
  # todo: error if inner is a flask route, i.e. they're in the wrong order
  @functools.wraps(inner)
  def wrapped(*args, **kwargs):
    if 'sessionid' not in flask.session:
      return flask.redirect(flask.url_for('splash'))
    dets = get_session(flask.current_app.redis_sessions, flask.session['sessionid'])
    if not dets:
      # todo stat & log
      return flask.redirect(flask.url_for('splash'))
    else:
      flask.g.sesh = dets
    return inner(*args, **kwargs)
  return wrapped

def setup_logging():
  "startup hook to setup access logging under gunicorn"
  # because this doesn't happen under gunicorn
  logging.basicConfig(level=logging.INFO)
