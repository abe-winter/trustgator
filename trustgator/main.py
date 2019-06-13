"main.py -- entrypoint for flask"

import flask
from . import flaskhelp, auth, trustgraph
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

@app.route('/beta-splash')
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

# todo: timing stats
@app.route('/home')
@flaskhelp.require_session
def get_home():
  return flask.render_template('home.htm',
    articles={
      'global': trustgraph.global_articles(),
      'hop1': trustgraph.articles_1hop(flask.g.sesh['userid']),
      'hop2': trustgraph.articles_2hop(flask.g.sesh['userid']),
      'followers': trustgraph.articles_vouchers(flask.g.sesh['userid']),
    },
    rfcs={},
    username=flask.g.sesh.get('username'),
  )

# note: this is a POST so samesite cookie applies
@app.route('/logout', methods=['POST'])
@flaskhelp.require_session
def post_logout():
  auth.logout()
  return flask.redirect(flask.url_for('get_login'))

@app.route('/link')
@flaskhelp.require_session
def get_addlink():
  return flask.render_template('submit-link.htm', username=flask.g.sesh.get('username'))

@app.route('/link', methods=['POST'])
@flaskhelp.require_session
def post_link():
  return trustgraph.submit_link(flask.request.form)

@app.route('/link/<linkid>')
@flaskhelp.require_session
def get_link(linkid):
  dets = trustgraph.load_article(linkid)
  return flask.render_template('link.htm',
    username=flask.g.sesh.get('username'),
    **dets
  )

@app.route('/assert', methods=['POST'])
@flaskhelp.require_session
def post_assert():
  return trustgraph.submit_assert(flask.request.form)

@app.route('/assert/<assertid>')
@flaskhelp.require_session
def get_assert(assertid):
  assert_, vouches, vouch_counts = trustgraph.load_assertion(assertid)
  return flask.render_template('assert.htm',
    assert_=assert_,
    vouches=vouches,
    vouch_counts=vouch_counts,
    username=flask.g.sesh.get('username'),
    your_vouch=next((vouch for vouch in vouches if vouch['userid'] == flask.g.sesh['userid']), None),
  )

@app.route('/vouch', methods=['POST'])
@flaskhelp.require_session
def post_vouch():
  return trustgraph.submit_vouch(flask.request.form)

@app.route('/pubuser/<userid>')
@flaskhelp.require_session
def get_pubuser(userid):
  return 'todo: public page for user'

@app.route('/legal')
def get_legal():
  return flask.render_template('legal.htm',
    ocilla=CONF['emails']['ocilla'] or f'legal@{CONF["domain_name"]}'
  )
