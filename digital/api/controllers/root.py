import pecan
from pecan import rest
from wsme import types as wtypes

from digital.api.controllers import base
from digital.api.controllers import link
from digital.api.controllers import v1
from digital.api.controllers import versions
from digital.api import expose


class Version(base.APIBase):
    """An API version representation."""

    id = wtypes.text
    """The ID of the version, also acts as the release number"""

    links = [link.Link]
    """A Link that point to a specific version of the API"""

    status = wtypes.text
    """The current status of the version: CURRENT, SUPPORTED, UNSUPPORTED"""

    max_version = wtypes.text
    """The max microversion supported by this version"""

    min_version = wtypes.text
    """The min microversion supported by this version"""

    @staticmethod
    def convert(id, status, max, min):
        version = Version()
        version.id = id
        version.links = [link.Link.make_link('self', pecan.request.host_url,
                                             id, '', bookmark=True)]
        version.status = status
        version.max_version = max
        version.min_version = min
        return version


class Root(base.APIBase):

    name = wtypes.text
    """The name of the API"""

    description = wtypes.text
    """Some information about this API"""

    versions = [Version]
    """Links to all the versions available in this API"""

    @staticmethod
    def convert():
        root = Root()
        root.name = "Digital API"
        root.description = ("Digital is an project which aims to "
                            "provide digital management for industry-4.0.")
        root.versions = [Version.convert('v1', "CURRENT",
                                         versions.CURRENT_MAX_VER,
                                         versions.BASE_VER)]
        return root


class RootController(rest.RestController):

    _versions = ['v1']
    """All supported API versions"""

    _default_version = 'v1'
    """The default API version"""

    v1 = v1.Controller()

    @expose.expose(Root)
    def get(self):
        # NOTE: The reason why convert() it's being called for every
        #       request is because we need to get the host url from
        #       the request object to make the links.
        return Root.convert()

    @pecan.expose()
    def _route(self, args):
        """Overrides the default routing behavior.

        It redirects the request to the default version of the digital API
        if the version number is not specified in the url.
        """

        if args[0] and args[0] not in self._versions:
            args = [self._default_version] + args
        return super(RootController, self)._route(args)

