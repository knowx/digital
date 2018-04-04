from digital.api.middleware import auth_token
from digital.api.middleware import parsable_error


AuthTokenMiddleware = auth_token.AuthTokenMiddleware
ParsableErrorMiddleware = parsable_error.ParsableErrorMiddleware

__all__ = (AuthTokenMiddleware,
           ParsableErrorMiddleware)
