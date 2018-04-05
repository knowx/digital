import json
import six
from webob import exc


class HTTPNotAcceptableAPIVersion(exc.HTTPNotAcceptable):
    # subclass of :class:`~HTTPNotAcceptable`
    #
    # This indicates the resource identified by the request is only
    # capable of generating response entities which have content
    # characteristics not acceptable according to the accept headers
    # sent in the request.
    #
    # code: 406, title: Not Acceptable
    #
    # differences from webob.exc.HTTPNotAcceptable:
    #
    # - additional max and min version parameters
    # - additional error info for code, title, and links
    code = 406
    title = 'Not Acceptable'
    max_version = ''
    min_version = ''

    def __init__(self, detail=None, headers=None, comment=None,
                 body_template=None, max_version='', min_version='', **kw):

        super(HTTPNotAcceptableAPIVersion, self).__init__(
            detail=detail, headers=headers, comment=comment,
            body_template=body_template, **kw)

        self.max_version = max_version
        self.min_version = min_version

    def __call__(self, environ, start_response):
        for err_str in self.app_iter:
            err = {}
            try:
                err = json.loads(err_str.decode('utf-8'))
            except ValueError:
                pass

            links = {'rel': 'help', 'href': 'http://developer.openstack.org'
                     '/api-guide/compute/microversions.html'}

            err['max_version'] = self.max_version
            err['min_version'] = self.min_version
            err['code'] = "digital.microversion-unsupported"
            err['links'] = [links]
            err['title'] = "Requested microversion is unsupported"

        self.app_iter = [six.b(json.dumps(err))]
        self.headers['Content-Length'] = str(len(self.app_iter[0]))

        return super(HTTPNotAcceptableAPIVersion, self).__call__(
            environ, start_response)
