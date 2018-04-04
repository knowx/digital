
from oslo_config import cfg

from digital.common.x509 import extensions
from digital.i18n import _

ALLOWED_EXTENSIONS = ['"%s"' % e.value for e in extensions.Extensions]
DEFAULT_ALLOWED_EXTENSIONS = [
    extensions.Extensions.KEY_USAGE.value,
    extensions.Extensions.EXTENDED_KEY_USAGE.value,
    extensions.Extensions.SUBJECT_ALTERNATIVE_NAME.value,
    extensions.Extensions.BASIC_CONSTRAINTS.value,
    extensions.Extensions.SUBJECT_KEY_IDENTIFIER.value]

ALLOWED_KEY_USAGE = ['"%s"' % e.value[0] for e in extensions.KeyUsages]
DEFAULT_ALLOWED_KEY_USAGE = [
    extensions.KeyUsages.DIGITAL_SIGNATURE.value[0],
    extensions.KeyUsages.KEY_ENCIPHERMENT.value[0],
    extensions.KeyUsages.CONTENT_COMMITMENT.value[0]]

x509_group = cfg.OptGroup(name='x509',
                          title='Options for X509 in Digital')

x509_opts = [
    cfg.BoolOpt('allow_ca',
                default=False,
                help=_('Certificate can get the CA flag in x509 extensions.')),
    cfg.ListOpt('allowed_extensions',
                default=DEFAULT_ALLOWED_EXTENSIONS,
                help=_('List of allowed x509 extensions. Available values: '
                       '%s') % ', '.join(ALLOWED_EXTENSIONS)),
    cfg.ListOpt('allowed_key_usage',
                default=DEFAULT_ALLOWED_KEY_USAGE,
                help=_('List of allowed x509 key usage. Available values: '
                       '%s') % ', '.join(ALLOWED_KEY_USAGE)),
    cfg.IntOpt('term_of_validity',
               default=365 * 5,
               help=_('Number of days for which a certificate is valid.')),
    cfg.IntOpt('rsa_key_size',
               default=2048, help=_('Size of generated private key. '))]


def register_opts(conf):
    conf.register_group(x509_group)
    conf.register_opts(x509_opts, group=x509_group)


def list_opts():
    return {
        x509_group: x509_opts
    }
