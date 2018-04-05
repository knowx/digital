from oslo_log import log as logging
import pecan
from wsme import types as wtypes

from digital.api.controllers import base as controllers_base
from digital.api.controllers import link
from digital.api.controllers.v1 import digital_services
from digital.api.controllers import versions as ver
from digital.api import expose
from digital.api import http_error
from digital.i18n import _

LOG = logging.getLogger(__name__)

BASE_VERSION = 1

MIN_VER_STR = '%s %s' % (ver.Version.service_string, ver.BASE_VER)

MAX_VER_STR = '%s %s' % (ver.Version.service_string, ver.CURRENT_MAX_VER)

MIN_VER = ver.Version({ver.Version.string: MIN_VER_STR},
                      MIN_VER_STR, MAX_VER_STR)
MAX_VER = ver.Version({ver.Version.string: MAX_VER_STR},
                      MIN_VER_STR, MAX_VER_STR)


class MediaType(controllers_base.APIBase):
    """A media type representation."""

    base = wtypes.text
    type = wtypes.text

    def __init__(self, base, type):
        self.base = base
        self.type = type


class V1(controllers_base.APIBase):
    """The representation of the version 1 of the API."""

    id = wtypes.text
    """The ID of the version, also acts as the release number"""

    media_types = [MediaType]
    """An array of supcontainersed media types for this version"""

    links = [link.Link]
    """Links that point to a specific URL for this version and documentation"""

    digital_services = [link.Link]
    """Links to the digital-services resource"""

    @staticmethod
    def convert():
        v1 = V1()
        v1.id = "v1"
        v1.links = [link.Link.make_link('self', pecan.request.host_url,
                                        'v1', '', bookmark=True),
                    link.Link.make_link('describedby',
                                        'http://docs.knowx.com',
                                        'developer/digital/dev',
                                        'api-spec-v1.html',
                                        bookmark=True, type='text/html')]
        v1.media_types = [MediaType('application/json',
                          'application/vnd.digital.v1+json')]
        v1.digital_services = [link.Link.make_link('self', pecan.request.host_url,
                                            'digital_services', ''),
                        link.Link.make_link('bookmark',
                                            pecan.request.host_url,
                                            'digital_services', '',
                                            bookmark=True)]

        return v1
    

class Controller(controllers_base.Controller):
    """Version 1 API controller root."""

    digital_services = digital_services.DigitalServiceController()

    @expose.expose(V1)
    def get(self):
        # NOTE: The reason why convert() it's being called for every
        #       request is because we need to get the host url from
        #       the request object to make the links.
        return V1.convert()

    def _check_version(self, version, headers=None):
        if headers is None:
            headers = {}
        # ensure that major version in the URL matches the header
        if version.major != BASE_VERSION:
            raise http_error.HTTPNotAcceptableAPIVersion(_(
                "Mutually exclusive versions requested. Version %(ver)s "
                "requested but not supported by this service."
                "The supported version range is: "
                "[%(min)s, %(max)s].") % {'ver': version,
                                          'min': MIN_VER_STR,
                                          'max': MAX_VER_STR},
                headers=headers,
                max_version=str(MAX_VER),
                min_version=str(MIN_VER))
        # ensure the minor version is within the supported range
        if version < MIN_VER or version > MAX_VER:
            raise http_error.HTTPNotAcceptableAPIVersion(_(
                "Version %(ver)s was requested but the minor version is not "
                "supported by this service. The supported version range is: "
                "[%(min)s, %(max)s].") % {'ver': version, 'min': MIN_VER_STR,
                                          'max': MAX_VER_STR},
                headers=headers,
                max_version=str(MAX_VER),
                min_version=str(MIN_VER))

    @pecan.expose()
    def _route(self, args):
        version = ver.Version(
            pecan.request.headers, MIN_VER_STR, MAX_VER_STR)

        # Always set the basic version headers
        pecan.response.headers[ver.Version.min_string] = MIN_VER_STR
        pecan.response.headers[ver.Version.max_string] = MAX_VER_STR
        pecan.response.headers[ver.Version.string] = " ".join(
            [ver.Version.service_string, str(version)])
        pecan.response.headers["vary"] = ver.Version.string

        # assert that requested version is supported
        self._check_version(version, pecan.response.headers)
        pecan.request.version = version
        if pecan.request.body:
            msg = ("Processing request: url: %(url)s, %(method)s, "
                   "body: %(body)s" %
                   {'url': pecan.request.url,
                    'method': pecan.request.method,
                    'body': pecan.request.body})
            LOG.debug(msg)

        return super(Controller, self)._route(args)


__all__ = (Controller)
