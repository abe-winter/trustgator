"main.py -- entrypoint for flask"

import flask
from . import flaskhelp, auth
from .util import CONF

app = flask.Flask(__name__)
app.secret_key = CONF['flask']['secret_key']
app.before_first_request(flaskhelp.setup_logging)
app.before_first_request(flaskhelp.setup_db)
app.before_first_request(flaskhelp.setup_redis)
app.config.update(
  SESSION_COOKIE_SECURE=CONF['mode'] != 'local',
  SESSION_COOKIE_HTTPONLY=True,
  SESSION_COOKIE_SAMESITE='Lax',
)

@app.route('/')
def splash():
  return flask.send_from_directory(app.static_folder, 'splash.htm')

@app.route('/vitals')
def vitals():
  "this is a health route; preferred temp for a croc is in the 30s"
  return '{"temp": "32C"}'

@app.route('/join')
def get_join():
  return flask.send_from_directory(app.static_folder, 'join.htm')
  raise NotImplementedError

@app.route('/join', methods=['POST'])
def post_join():
  ret = auth.create_acct(flask.request.form, login_also=True)
  if ret['errors']:
    return flask.render_template('multi-error.htm', errors=ret['errors'])
  flask.session['sessionid'] = ret['sessionid']
  return flask.redirect(flask.url_for('get_home'))

@app.route('/login')
def get_login():
  return flask.send_from_directory(app.static_folder, 'login.htm')

@app.route('/login', methods=['POST'])
def post_login():
  return auth.login(flask.request.form)

@app.route('/home')
@flaskhelp.require_session
def get_home():
  return flask.render_template('home.htm', username=flask.g.sesh.get('username'))

# note: this is a POST so samesite cookie applies
@app.route('/logout', methods=['POST'])
@flaskhelp.require_session
def post_logout():
  auth.logout()
  return flask.redirect(flask.url_for('get_login'))
