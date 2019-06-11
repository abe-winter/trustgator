import bcrypt, flask, psycopg2, sqlalchemy as sa, json, uuid
from . import util, flaskhelp

CREATE_RATE = util.RateLimiter('create_acct', max_per_minute=10)

def create_session(userid: str):
  sessionid = str(uuid.uuid4())
  val = json.dumps({'userid': userid})
  flask.current_app.redis_sessions.set(
    flaskhelp.session_key(sessionid),
    val,
    ex=30 * 86400
  )
  return sessionid

def session_key(sessionid: str) -> str:
  return json.dumps({'sessionid': sessionid})
  raise NotImplementedError

def create_acct(form: dict, login_also=False) -> dict:
  "returns dict of {sessionid: Optional[str], errors: List[str]}"
  errors = []
  if len(form['username']) > 64:
    errors.append("max len for username = 64 chars")
  if not form['password'] or len(form['password']) > 64:
    errors.append("max len for password = 64 chars")
  if form['email'] and '@' not in form['email']:
    errors.append("email needs an @")
  if not CREATE_RATE.check():
    errors.append('too many new accounts! sorry! try again later or get on the waitlist at <a href="/waitlist">waitlist</a> or ask a friend for an invite')
  if errors:
    return {'sessionid': None, 'errors': errors}
  hashed = bcrypt.hashpw(form['password'].encode('utf8'), bcrypt.gensalt())
  try:
    with flask.current_app.queries.transaction():
      ret = flask.current_app.queries.insert_user(username=form['username'], password=hashed, email=form['email'])
      return {'sessionid': create_session(str(ret['userid'])), 'errors': []}
  except sa.exc.IntegrityError as err:
    if isinstance(err.orig, psycopg2.errors.UniqueViolation):
      print(err) # so logging picks it up
      return {'sessionid': None, 'errors': ['that username already exists']}
    else:
      raise
