from oslo_config import cfg

from digital.conf import api
from digital.conf import barbican
from digital.conf import certificates
from digital.conf import database
from digital.conf import keystone
from digital.conf import paths
from digital.conf import profiler
from digital.conf import services
from digital.conf import trust
from digital.conf import utils
from digital.conf import x509

CONF = cfg.CONF

api.register_opts(CONF)
barbican.register_opts(CONF)
certificates.register_opts(CONF)
database.register_opts(CONF)
keystone.register_opts(CONF)
paths.register_opts(CONF)
profiler.register_opts(CONF)
services.register_opts(CONF)
trust.register_opts(CONF)
utils.register_opts(CONF)
x509.register_opts(CONF)

