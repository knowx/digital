from oslo_config import cfg

from digital.conf import api
from digital.conf import database
from digital.conf import paths

CONF = cfg.CONF

api.register_opts(CONF)
database.register_opts(CONF)
paths.register_opts(CONF)
