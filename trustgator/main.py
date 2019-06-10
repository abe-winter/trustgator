"main.py -- entrypoint for flask"

import flask
from . import flaskhelp
from .util import CONF

app = flask.Flask(__name__)
app.secret_key = CONF['flask']['secret_key']
app.before_first_request(flaskhelp.setup_logging)
app.before_first_request(flaskhelp.setup_db)
app.before_first_request(flaskhelp.setup_redis)

@app.route('/')
def splash():
  return flask.send_from_directory(app.static_folder, 'splash.htm')

@app.route('/vitals')
def vitals():
  "this is a health route; preferred temp for a croc is in the 30s"
  return '{"temp": "32C"}'
