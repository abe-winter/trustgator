import statsd, varyaml, os

CONF = varyaml.load(open(os.environ.get('VARYAML', 'varyaml.yml')))

STATS = statsd.StatsClient(prefix='tgtr.')
