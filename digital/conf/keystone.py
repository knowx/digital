from keystoneauth1 import loading as ka_loading
from oslo_config import cfg

CFG_GROUP = 'keystone_auth'
CFG_LEGACY_GROUP = 'keystone_authtoken'

legacy_session_opts = {
    'certfile': [cfg.DeprecatedOpt('certfile', CFG_LEGACY_GROUP)],
    'keyfile': [cfg.DeprecatedOpt('keyfile', CFG_LEGACY_GROUP)],
    'cafile': [cfg.DeprecatedOpt('cafile', CFG_LEGACY_GROUP)],
    'insecure': [cfg.DeprecatedOpt('insecure', CFG_LEGACY_GROUP)],
    'timeout': [cfg.DeprecatedOpt('timeout', CFG_LEGACY_GROUP)],
}

keystone_auth_group = cfg.OptGroup(name=CFG_GROUP,
                                   title='Options for Keystone in Digital')


def register_opts(conf):
    # FIXME(pauloewerton): remove import of authtoken group and legacy options
    # after deprecation period
    conf.import_group(CFG_LEGACY_GROUP, 'keystonemiddleware.auth_token')
    ka_loading.register_auth_conf_options(conf, CFG_GROUP)
    ka_loading.register_session_conf_options(
        conf, CFG_GROUP, deprecated_opts=legacy_session_opts)
    conf.set_default('auth_type', default='password', group=CFG_GROUP)


def list_opts():
    keystone_auth_opts = (ka_loading.get_auth_common_conf_options() +
                          ka_loading.get_auth_plugin_conf_options('password'))
    return {
        keystone_auth_group: keystone_auth_opts
    }