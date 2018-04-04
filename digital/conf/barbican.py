from oslo_config import cfg

from digital.i18n import _

barbican_group = cfg.OptGroup(name='barbican_client',
                              title='Options for the Barbican client')

barbican_client_opts = [
    cfg.StrOpt('region_name',
               help=_('Region in Identity service catalog to use for '
                      'communication with the OpenStack service.')),
    cfg.StrOpt('endpoint_type',
               default='publicURL',
               help=_('Type of endpoint in Identity service catalog to use '
                      'for communication with the OpenStack service.'))]


def register_opts(conf):
    conf.register_group(barbican_group)
    conf.register_opts(barbican_client_opts, group=barbican_group)


def list_opts():
    return {
        barbican_group: barbican_client_opts
    }
