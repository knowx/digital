from oslo_config import cfg

from digital.i18n import _

service_opts = [
    cfg.StrOpt('host',
               help=_('Name of this node. This can be an opaque identifier. '
                      'It is not necessarily a hostname, FQDN, or IP address. '
                      'However, the node name must be valid within '
                      'an AMQP key, and if using ZeroMQ, a valid '
                      'hostname, FQDN, or IP address.')),
]


def register_opts(conf):
    conf.register_opts(service_opts)


def list_opts():
    return {
        "DEFAULT": service_opts
    }