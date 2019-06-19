import bcrypt, flask, psycopg2, sqlalchemy as sa, rapidjson, uuid, binascii, os
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

class InviteCodeFailure(Exception): pass

def create_acct(form: dict, login_also=False) -> dict:
  "returns dict of {sessionid: Optional[str], errors: List[str]}"
  errors = []
  if len(form['username']) > 64:
    errors.append("max len for username = 64 chars")
  if not form['password'] or len(form['password']) > 64:
    errors.append("max len for password = 64 chars")
  if form['email'] and '@' not in form['email']:
    errors.append("email needs an @")
  if util.CONF['invites']['invite_only']:
    if not form['invite_code']:
      errors.append("the site is in invite_only mode, you need an invitation")
  elif not CREATE_RATE.check():
    errors.append('too many new accounts! sorry! try again later or get on the waitlist at <a href="/waitlist">waitlist</a> or ask a friend for an invite')
  if errors:
    # todo: stat
    return {'sessionid': None, 'errors': errors}
  hashed = bcrypt.hashpw(form['password'].encode('utf8'), bcrypt.gensalt())
  queries = flask.current_app.queries
  try:
    with queries.transaction():
      ret = queries.insert_user(username=form['username'], password=hashed, email=form['email'])
      if form['invite_code']:
        invite = queries.get_invite(code=form['invite_code'])
        # note: throwing here so the tx rolls back
        if not invite:
          raise InviteCodeFailure("invite code not found -- did you type it wrong maybe?")
        elif invite['redeemed_userid']:
          raise InviteCodeFailure("invite code already used")
        queries.use_invite(code=form['invite_code'], userid=str(ret['userid']))
        # todo: make sure updated row count is 1 above
      dets = {'username': form['username'], 'userid': str(ret['userid']), 'admin': ret['admin']}
      # todo: stat
      if login_also:
        return {'sessionid': create_session(dets), 'errors': []}
      else:
        return {'sessionid': None, errors: []}
  except sa.exc.IntegrityError as err:
    # pylint: disable=no-member
    if isinstance(err.orig, psycopg2.errors.UniqueViolation):
      print(err) # so logging picks it up
      return {'sessionid': None, 'errors': ['that username already exists']}
    else:
      raise
  except InviteCodeFailure as err:
    return {'errors': [err.args[0]]}

# todo: timing stat
def login(form: dict) -> str:
  row = flask.current_app.queries.get_user(username=form['username'])
  if not row or not bcrypt.checkpw(form['password'].encode('utf8'), row['password'].tobytes()):
    # todo: stat
    flask.abort(403)
  sessionid = create_session({
    'userid': row['userid'],
    'username': row['username'],
    'admin': row['admin'],
  })
  # todo: stat
  flask.session['sessionid'] = sessionid
  return flask.redirect(flask.url_for('get_home'))

def logout():
  # todo: stat
  sessionid = flask.session.pop('sessionid')
  flask.current_app.redis_sessions.delete(flaskhelp.session_key(sessionid))

def issue_invite(issuing_user: str, ignore_max=False, queries=None):
  "ignore_max is for manually granting these to power users"
  if not queries: # i.e. if not in shell context
    if not invites_allowed():
      return "Sorry, this server has invites.restrict = true"
    queries = flask.current_app.queries
  with queries.transaction():
    if not ignore_max:
      ninvites = len(list(queries.get_invites(userid=issuing_user)))
      if ninvites >= util.CONF['invites']['max_per_user']:
        return 'error: you hit the max'
    code = binascii.hexlify(os.urandom(5)).decode('ascii')
    queries.insert_invite(userid=issuing_user, code=code)
  return flask.redirect(flask.url_for('get_invites'))

def invites_allowed() -> bool:
  return flask.g.sesh.get('admin') \
    or not util.CONF['invites']['restrict'] \
    or bool(flask.current_app.queries.is_invitee(userid=flask.g.sesh['userid'])['count'])

def submit_allowed() -> bool:
  queries = flask.current_app.queries
  userid = flask.g.sesh['userid']
  return flask.g.sesh.get('admin') \
    or not util.CONF.get('gate_submits') \
    or bool(queries.ever_vouched(userid=userid)['count']) \
    or bool(queries.is_invitee(userid=userid)['count'])
