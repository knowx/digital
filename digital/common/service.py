from oslo_log import log as logging

from digital.common import config
from digital import conf

CONF = conf.CONF


def prepare_service(argv=None):
    if argv is None:
        argv = []
    logging.register_options(CONF)
    config.parse_args(argv)
    config.set_config_defaults()

    logging.setup(CONF, 'digital')