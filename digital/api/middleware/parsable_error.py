import json
import six

from digital.i18n import _


class ParsableErrorMiddleware(object):
    """Replace error body with something the client can parse."""
    def __init__(self, app):
        self.app = app

    def _update_errors(self, app_iter, status_code):
        errs = []
        for err_str in app_iter:
            err = {}
            try:
                err = json.loads(err_str.decode('utf-8'))
            except ValueError:
                pass

            if 'title' in err and 'description' in err:
                title = err['title']
                desc = err['description']
            elif 'faultstring' in err:
                title = err['faultstring'].split('.', 1)[0]
                desc = err['faultstring']
            else:
                title = ''
                desc = ''

            code = err['faultcode'].lower() if 'faultcode' in err else ''

            # if already formatted by custom exception, don't update
            if 'min_version' in err:
                errs.append(err)
            else:
                errs.append({
                    'request_id': '',
                    'code': code,
                    'status': status_code,
                    'title': title,
                    'detail': desc,
                    'links': []})

        return errs

    def __call__(self, environ, start_response):
        # Request for this state, modified by replace_start_response()
        # and used when an error is being reported.
        state = {}

        def replacement_start_response(status, headers, exc_info=None):
            """Overrides the default response to make errors parsable."""
            try:
                status_code = int(status.split(' ')[0])
                state['status_code'] = status_code
            except (ValueError, TypeError):  # pragma: nocover
                raise Exception(_(
                    'ErrorDocumentMiddleware received an invalid '
                    'status %s') % status)
            else:
                if (state['status_code'] // 100) not in (2, 3):
                    # Remove some headers so we can replace them later
                    # when we have the full error message and can
                    # compute the length.
                    headers = [(h, v)
                               for (h, v) in headers
                               if h not in ('Content-Length', 'Content-Type')
                               ]
                # Save the headers in case we need to modify them.
                state['headers'] = headers

                return start_response(status, headers, exc_info)

        app_iter = self.app(environ, replacement_start_response)

        if (state['status_code'] // 100) not in (2, 3):
            errs = self._update_errors(app_iter, state['status_code'])
            body = [six.b(json.dumps({'errors': errs}))]
            state['headers'].append(('Content-Type', 'application/json'))
            state['headers'].append(('Content-Length', str(len(body[0]))))

        else:
            body = app_iter
        return body
