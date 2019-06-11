import bcrypt, flask, psycopg2, sqlalchemy as sa, rapidjson, uuid
from . import util, flaskhelp

CREATE_RATE = util.RateLimiter('create_acct', max_per_minute=10)

def create_session(dets: dict):
  sessionid = uuid.uuid4()
  val = rapidjson.dumps(dets, uuid_mode=rapidjson.UM_CANONICAL)
  # todo: fail if already set (i.e. uuid collision)
  flask.current_app.redis_sessions.set(
    flaskhelp.session_key(sessionid),
    val,
    ex=30 * 86400
  )
  return sessionid

def create_acct(form: dict, login_also=False) -> dict:
  "returns dict of {sessionid: Optional[str], errors: List[str]}"
  errors = []
  if util.CONF['invites']['invite_only']:
    # todo: better error message
    raise NotImplementedError("todo: invite-only mode")
  if len(form['username']) > 64:
    errors.append("max len for username = 64 chars")
  if not form['password'] or len(form['password']) > 64:
    errors.append("max len for password = 64 chars")
  if form['email'] and '@' not in form['email']:
    errors.append("email needs an @")
  if not CREATE_RATE.check():
    errors.append('too many new accounts! sorry! try again later or get on the waitlist at <a href="/waitlist">waitlist</a> or ask a friend for an invite')
  if errors:
    # todo: stat
    return {'sessionid': None, 'errors': errors}
  hashed = bcrypt.hashpw(form['password'].encode('utf8'), bcrypt.gensalt())
  try:
    with flask.current_app.queries.transaction():
      ret = flask.current_app.queries.insert_user(username=form['username'], password=hashed, email=form['email'])
      dets = {'username': form['username'], 'userid': str(ret['userid'])}
      # todo: stat
      if login_also:
        return {'sessionid': create_session(dets), 'errors': []}
      else:
        return {'sessionid': None, errors: []}
  except sa.exc.IntegrityError as err:
    if isinstance(err.orig, psycopg2.errors.UniqueViolation):
      print(err) # so logging picks it up
      return {'sessionid': None, 'errors': ['that username already exists']}
    else:
      raise

# todo: timing stat
def login(form: dict) -> str:
  row = flask.current_app.queries.get_user(username=form['username'])
  if not row or not bcrypt.checkpw(form['password'].encode('utf8'), row['password'].tobytes()):
    # todo: stat
    flask.abort(403)
  sessionid = create_session({
    'userid': row['userid'],
    'username': row['username'],
  })
  # todo: stat
  flask.session['sessionid'] = sessionid
  return flask.redirect(flask.url_for('get_home'))

def logout():
  # todo: stat
  sessionid = flask.session.pop('sessionid')
  flask.current_app.redis_sessions.delete(flaskhelp.session_key(sessionid))
