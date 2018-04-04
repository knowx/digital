from oslo_config import cfg

api_group = cfg.OptGroup(name='api',
                         title='Options for the digital-api service')

api_service_opts = [
    cfg.PortOpt('port',
                default=8080,
                help='The port for the Digital API server.'),
    cfg.IPOpt('host',
              default='127.0.0.1',
              help='The listen IP for the Digital API server.'),
    cfg.IntOpt('max_limit',
               default=1000,
               help='The maximum number of items returned in a single '
                    'response from a collection resource.'),
    cfg.StrOpt('api_paste_config',
               default="api-paste.ini",
               help="Configuration file for WSGI definition of API."
               ),
    cfg.StrOpt('ssl_cert_file',
               help="This option allows setting path to the SSL certificate "
                    "of API server. "),
    cfg.StrOpt('ssl_key_file',
               help="This option specifies the path to the file where SSL "
                    "private key of API server is stored when SSL is in "
                    "effect. "),
    cfg.BoolOpt('enabled_ssl',
                default=False,
                help='Enable SSL Digital API service'),
    cfg.IntOpt('workers',
               help='The maximum number of digital-api processes to '
                    'fork and run. Default to number of CPUs on the host.')
]


def register_opts(conf):
    conf.register_group(api_group)
    conf.register_opts(api_service_opts, group=api_group)


def list_opts():
    return {
        api_group: api_service_opts
    }