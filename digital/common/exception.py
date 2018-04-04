import functools
import sys
import six

from keystoneclient import exceptions as keystone_exceptions
from oslo_config import cfg
from oslo_log import log as logging

from digital import conf
from digital.i18n import _


LOG = logging.getLogger(__name__)

CONF = conf.CONF


try:
    CONF.import_opt('fatal_exception_format_errors',
                    'oslo_versionedobjects.exception')
except cfg.NoSuchOptError as e:
    CONF.import_opt('fatal_exception_format_errors',
                    'oslo_versionedobjects.exception',
                    group='oslo_versionedobjects')


def wrap_keystone_exception(func):
    """Wrap keystone exceptions and throw Digital specific exceptions."""
    @functools.wraps(func)
    def wrapped(*args, **kw):
        try:
            return func(*args, **kw)
        except keystone_exceptions.AuthorizationFailure:
            raise AuthorizationFailure(
                client=func.__name__, message="reason: %s" % sys.exc_info()[1])
        except keystone_exceptions.ClientException:
            raise AuthorizationFailure(
                client=func.__name__,
                message="unexpected keystone client error occurred: %s"
                        % sys.exc_info()[1])
    return wrapped


class DigitalException(Exception):
    """Base Digital Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.

    """
    message = _("An unknown exception occurred.")
    code = 500

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs and hasattr(self, 'code'):
            self.kwargs['code'] = self.code

        if message:
            self.message = message

        try:
            self.message = self.message % kwargs
        except Exception:
            # kwargs doesn't match a variable in the message
            # log the issue and the kwargs
            LOG.exception('Exception in string format operation, '
                          'kwargs: %s', kwargs)
            try:
                if CONF.fatal_exception_format_errors:
                    raise
            except cfg.NoSuchOptError:
                # Note: work around for Bug: #1447873
                if CONF.oslo_versionedobjects.fatal_exception_format_errors:
                    raise

        super(DigitalException, self).__init__(self.message)

    def __str__(self):
        if six.PY3:
            return self.message
        return self.message.encode('utf-8')

    def __unicode__(self):
        return self.message

    def format_message(self):
        if self.__class__.__name__.endswith('_Remote'):
            return self.args[0]
        else:
            return six.text_type(self)
        
        
class ObjectNotFound(DigitalException):
    message = _("The %(name)s %(id)s could not be found.")
    code = 404


class ProjectNotFound(ObjectNotFound):
    message = _("The %(name)s %(id)s could not be found.")


class ResourceNotFound(ObjectNotFound):
    message = _("The %(name)s resource %(id)s could not be found.")


class AuthorizationFailure(DigitalException):
    message = _("%(client)s connection failed. %(message)s")
    code = 403


class Invalid(DigitalException):
    message = _("Unacceptable parameters.")
    code = 400


class InvalidUUID(Invalid):
    message = _("Expected a uuid but received %(uuid)s.")


class InvalidName(Invalid):
    message = _("Expected a name but received %(name)s.")
    

class NotAuthorized(DigitalException):
    message = _("Not authorized.")
    code = 403
    

class PolicyNotAuthorized(NotAuthorized):
    message = _("Policy doesn't allow %(action)s to be performed.")
    

class TrustCreateFailed(DigitalException):
    message = _("Failed to create trust for trustee %(trustee_user_id)s.")


class TrustDeleteFailed(DigitalException):
    message = _("Failed to delete trust %(trust_id)s.")


class TrusteeCreateFailed(DigitalException):
    message = _("Failed to create trustee %(username)s "
                "in domain %(domain_id)s")


class TrusteeDeleteFailed(DigitalException):
    message = _("Failed to delete trustee %(trustee_id)s")


class InvalidParameterValue(Invalid):
    message = _("%(err)s")

    
class RegionsListFailed(DigitalException):
    message = _("Failed to list regions.")


class ConfigInvalid(Invalid):
    message = _("Invalid configuration file. %(error_msg)s")