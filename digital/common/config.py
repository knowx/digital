from oslo_middleware import cors

from digital.common import rpc
from digital import conf
from digital import version

CONF = conf.CONF


def parse_args(argv, default_config_files=None):
    rpc.set_defaults(control_exchange='digital')
    CONF(argv[1:],
         project='digital',
         version=version.current_version,
         default_config_files=default_config_files)
    rpc.init(CONF)


def set_config_defaults():
    """This method updates all configuration default values."""
    set_cors_middleware_defaults()


def set_cors_middleware_defaults():
    """Update default configuration options for oslo.middleware."""
    cors.set_defaults(
        allow_headers=['X-Auth-Token',
                       'X-Identity-Status',
                       'X-Roles',
                       'X-Service-Catalog',
                       'X-User-Id',
                       'X-Tenant-Id',
                       'X-OpenStack-Request-ID',
                       'X-Server-Management-Url'],
        expose_headers=['X-Auth-Token',
                        'X-Subject-Token',
                        'X-Service-Token',
                        'X-OpenStack-Request-ID',
                        'X-Server-Management-Url'],
        allow_methods=['GET',
                       'PUT',
                       'POST',
                       'DELETE',
                       'PATCH']
    )
