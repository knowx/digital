import itertools
from oslo_config import cfg

DEFAULT_CERT_MANAGER = 'barbican'
TLS_STORAGE_DEFAULT = '/var/lib/digital/certificates/'

certificates_group = cfg.OptGroup(name='certificates',
                                  title='Certificate options for the '
                                        'cert manager.')

cert_manager_opts = [
    cfg.StrOpt('cert_manager_type',
               default=DEFAULT_CERT_MANAGER,
               help='Certificate Manager plugin. '
                    'Defaults to {0}.'.format(DEFAULT_CERT_MANAGER))
]

local_cert_manager_opts = [
    cfg.StrOpt('storage_path',
               default=TLS_STORAGE_DEFAULT,
               help='Absolute path of the certificate storage directory. '
                    'Defaults to /var/lib/digital/certificates/.')
]

ALL_OPTS = list(itertools.chain(
    cert_manager_opts,
    local_cert_manager_opts
))


def register_opts(conf):
    conf.register_group(certificates_group)
    conf.register_opts(ALL_OPTS, group=certificates_group)


def list_opts():
    return {
        certificates_group: ALL_OPTS
    }
