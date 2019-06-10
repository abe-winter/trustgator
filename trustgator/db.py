import subprocess, sqlalchemy as sa
from .util import CONF

def set_missing_host(key1, key2, make_cmd):
  "this is to set container hostnames in local docker mode"
  if not CONF[key1].get(key2):
    # note: --no-print-directory below is necessary under another make (i.e. make test)
    CONF[key1][key2] = subprocess.check_output(f'make {make_cmd} --no-print-directory', shell=True).strip().decode()

set_missing_host('db_args', 'host', 'db-host')
set_missing_host('redis', 'sessions', 'redis-host')
set_missing_host('redis', 'cache', 'redis-host')

def db_url():
  return sa.engine.url.URL(**CONF['db_args'])
