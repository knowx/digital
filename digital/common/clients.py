from barbicanclient.v1 import client as barbicanclient
from keystoneauth1.exceptions import catalog

from oslo_log import log as logging

from digital.common import exception
from digital.common import keystone

from digital import conf

CONF = conf.CONF
LOG = logging.getLogger(__name__)


class OpenStackClients(object):
    """Convenience class to create and cache client instances."""

    def __init__(self, context):
        self.context = context
        self._keystone = None

    def url_for(self, **kwargs):
        return self.keystone().session.get_endpoint(**kwargs)

    def digital_url(self):
        endpoint_type = self._get_client_option('digital', 'endpoint_type')
        region_name = self._get_client_option('digital', 'region_name')
        try:
            return self.url_for(service_type='digital-infra',
                                interface=endpoint_type,
                                region_name=region_name)
        except catalog.EndpointNotFound:
            url = self.url_for(service_type='digital',
                               interface=endpoint_type,
                               region_name=region_name)
            LOG.warning('Service type "digital" is deprecated and will '
                        'be removed in a subsequent release')
            return url

    @property
    def auth_url(self):
        return self.keystone().auth_url

    @property
    def auth_token(self):
        return self.context.auth_token or self.keystone().auth_token

    def keystone(self):
        if self._keystone:
            return self._keystone

        self._keystone = keystone.KeystoneClientV3(self.context)
        return self._keystone

    def _get_client_option(self, client, option):
        return getattr(getattr(CONF, '%s_client' % client), option)

    @exception.wrap_keystone_exception
    def barbican(self):
        if self._barbican:
            return self._barbican

        endpoint_type = self._get_client_option('barbican', 'endpoint_type')
        region_name = self._get_client_option('barbican', 'region_name')
        endpoint = self.url_for(service_type='key-manager',
                                interface=endpoint_type,
                                region_name=region_name)
        session = self.keystone().session
        self._barbican = barbicanclient.Client(session=session,
                                               endpoint=endpoint)

        return self._barbican
