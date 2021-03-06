"main.py -- entrypoint for flask"

import flask
from . import flaskhelp, auth, trustgraph
from .util import CONF, STATS

app = flask.Flask(__name__)
app.secret_key = CONF['flask']['secret_key']
app.before_first_request(flaskhelp.setup_logging)
app.before_first_request(flaskhelp.setup_db)
app.before_first_request(flaskhelp.setup_redis)
app.config.update(
  SESSION_COOKIE_SECURE=CONF['mode'] != 'local',
  SESSION_COOKIE_HTTPONLY=True,
  # note: lax mode means all state-changing routes have to be non-GET
  SESSION_COOKIE_SAMESITE='Lax',
)

RENDERED = {
  'splash': app.jinja_env.get_or_select_template('splash.htm').render(),
  'join': app.jinja_env.get_or_select_template('join.htm').render(),
  'login': app.jinja_env.get_or_select_template('login.htm').render(),
}

@app.route('/beta-splash')
@app.route('/')
def splash():
  return RENDERED['splash']

@app.route('/vitals')
def vitals():
  "this is a health route; preferred temp for a croc is in the 30s"
  return '{"temp": "32C"}'

@app.route('/join')
def get_join():
  return RENDERED['join']

@app.route('/join', methods=['POST'])
def post_join():
  ret = auth.create_acct(flask.request.form, login_also=True)
  if ret['errors']:
    return flask.render_template('multi-error.htm', errors=ret['errors'])
  flask.session['sessionid'] = ret['sessionid']
  return flask.redirect(flask.url_for('get_home'))

@app.route('/login')
def get_login():
  return RENDERED['login']

@app.route('/login', methods=['POST'])
def post_login():
  return auth.login(flask.request.form)

@app.route('/home')
@flaskhelp.require_session
@STATS.timer('route.get_home')
def get_home():
  return flask.render_template('home.htm',
    articles={
      'global': trustgraph.global_articles(),
      'hop1': trustgraph.articles_1hop(flask.g.sesh['userid']),
      'hop2': trustgraph.articles_2hop(flask.g.sesh['userid']),
      'followers': trustgraph.articles_vouchers(flask.g.sesh['userid']),
    },
    rfcs={},
    userid=flask.g.sesh.get('userid'),
    show_invites=auth.invites_allowed(),
    show_submit=auth.submit_allowed(),
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
  return flask.render_template('submit-link.htm')

@app.route('/link', methods=['POST'])
@flaskhelp.require_session
def post_link():
  return trustgraph.submit_link(flask.request.form)

@app.route('/link/<linkid>')
@flaskhelp.require_session
def get_link(linkid):
  dets = trustgraph.load_article(linkid)
  return flask.render_template('link.htm',
    userid=flask.g.sesh['userid'],
    deletable=flask.g.sesh['userid'] == dets['link']['userid'] and dets['age_seconds'] < CONF['delete_minutes']['link'] * 60,
    delete_window=CONF['delete_minutes']['link'],
    can_flag=auth.submit_allowed(),
    **dets
  )

@app.route('/overlay/<linkid>')
@flaskhelp.require_session
def get_overlay(linkid):
  dets = trustgraph.load_overlay(linkid)
  return flask.render_template('overlay.htm', **dets)

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
    your_vouch=next((vouch for vouch in vouches if vouch['userid'] == flask.g.sesh['userid']), None),
  )

@app.route('/vouch', methods=['POST'])
@flaskhelp.require_session
def post_vouch():
  return trustgraph.submit_vouch(flask.request.form)

@app.route('/pubuser/<userid>')
@flaskhelp.require_session
def get_pubuser(userid):
  return flask.render_template('pubuser.htm',
    pubuser=trustgraph.load_pubuser(userid),
  )

@app.route('/legal')
def get_legal():
  return flask.render_template('legal.htm',
    ocilla=CONF['emails']['ocilla'] or f'legal@{CONF["domain_name"]}'
  )

@app.route('/settings')
@flaskhelp.require_session
def get_settings():
  return flask.render_template('settings.htm')

@app.route('/trustnet')
@flaskhelp.require_session
def get_trustnet():
  return flask.render_template('trustnet.htm',
    net=trustgraph.load_trustnet(flask.g.sesh['userid']),
  )

@app.route('/invites')
@flaskhelp.require_session
def get_invites():
  invites = list(flask.current_app.queries.get_invites(userid=flask.g.sesh['userid']))
  return flask.render_template('invites.htm', invites=invites)

@app.route('/invites', methods=['POST'])
@flaskhelp.require_session
def post_invites():
  return auth.issue_invite(flask.g.sesh['userid'])

@app.route('/link/del', methods=['POST'])
@flaskhelp.require_session
def post_link_del():
  return trustgraph.delete_link(flask.request.form)

@app.route('/assert/del', methods=['POST'])
@flaskhelp.require_session
def post_assert_del():
  return trustgraph.delete_assert(flask.request.form)

@app.route('/link/flag/<linkid>')
@flaskhelp.require_session
def get_flag(linkid):
  return flask.render_template('flag.htm',
    link=flask.current_app.queries.load_link(linkid=linkid),
    kind='link',
  )

@app.route('/link/flags/<linkid>')
@flaskhelp.require_session
def get_flags(linkid):
  queries = flask.current_app.queries
  return flask.render_template('flags.htm',
    link=queries.load_link(linkid=linkid),
    flags=queries.link_flags(linkid=linkid),
    kind='link',
  )

@app.route('/link/flag/<linkid>', methods=['POST'])
@flaskhelp.require_session
def post_flag(linkid):
  return trustgraph.flag_link(linkid, flask.request.form)

@app.route('/assert/flag/<assertid>')
@flaskhelp.require_session
def get_flag_assert(assertid):
  raise NotImplementedError

@app.route('/assert/flag/<assertid>', methods=['POST'])
@flaskhelp.require_session
def post_flag_assert(assertid):
  raise NotImplementedError
