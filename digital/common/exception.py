import functools
import sys

from keystoneclient import exceptions as keystone_exceptions
from oslo_config import cfg
from oslo_log import log as logging
import six

from digital import conf
from digital.i18n import _


LOG = logging.getLogger(__name__)

CONF = conf.CONF

try:
    CONF.import_opt('fatal_exception_format_errors',
                    'oslo_versionedobjects.exception')
except cfg.NoSuchOptError as e:
    # Note:work around for digital run against master branch
    # in devstack gate job, as digital not branched yet
    # verisonobjects kilo/master different version can
    # cause issue here. As it changed import group. So
    # add here before branch to prevent gate failure.
    # Bug: #1447873
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


class InvalidDiscoveryURL(Invalid):
    message = _("Received invalid discovery URL '%(discovery_url)s' for "
                "discovery endpoint '%(discovery_endpoint)s'.")


class GetDiscoveryUrlFailed(DigitalException):
    message = _("Failed to get discovery url from '%(discovery_endpoint)s'.")


class InvalidClusterDiscoveryURL(Invalid):
    message = _("Invalid discovery URL '%(discovery_url)s'.")


class InvalidClusterSize(Invalid):
    message = _("Expected cluster size %(expect_size)d but get cluster "
                "size %(size)d from '%(discovery_url)s'.")


class GetClusterSizeFailed(DigitalException):
    message = _("Failed to get the size of cluster from '%(discovery_url)s'.")


class InvalidIdentity(Invalid):
    message = _("Expected an uuid or int but received %(identity)s.")


class InvalidCsr(Invalid):
    message = _("Received invalid csr %(csr)s.")


class InvalidSubnet(Invalid):
    message = _("Received invalid subnet %(subnet)s.")


class HTTPNotFound(ResourceNotFound):
    pass


class Conflict(DigitalException):
    message = _('Conflict.')
    code = 409


class ApiVersionsIntersect(Invalid):
    message = _("Version of %(name)s %(min_ver)s %(max_ver)s intersects "
                "with another versions.")


# Cannot be templated as the error syntax varies.
# msg needs to be constructed when raised.
class InvalidParameterValue(Invalid):
    message = _("%(err)s")


class PatchError(Invalid):
    message = _("Couldn't apply patch '%(patch)s'. Reason: %(reason)s")


class NotAuthorized(DigitalException):
    message = _("Not authorized.")
    code = 403


class PolicyNotAuthorized(NotAuthorized):
    message = _("Policy doesn't allow %(action)s to be performed.")


class InvalidMAC(Invalid):
    message = _("Expected a MAC address but received %(mac)s.")


class ConfigInvalid(Invalid):
    message = _("Invalid configuration file. %(error_msg)s")


class NotSupported(DigitalException):
    message = _("%(operation)s is not supported.")
    code = 400


class RequiredParameterNotProvided(Invalid):
    message = _("Required parameter %(heat_param)s not provided.")


class OperationInProgress(Invalid):
    message = _("Cluster %(cluster_name)s already has an operation in "
                "progress.")


class OSDistroFieldNotFound(ResourceNotFound):
    """The code here changed to 400 according to the latest document."""
    message = _("Image %(image_id)s doesn't contain os_distro field.")
    code = 400


class X509KeyPairNotFound(ResourceNotFound):
    message = _("A key pair %(x509keypair)s could not be found.")


class X509KeyPairAlreadyExists(Conflict):
    message = _("A key pair with UUID %(uuid)s already exists.")


class CertificateStorageException(DigitalException):
    message = _("Could not store certificate: %(msg)s")


class CertificateValidationError(Invalid):
    message = _("Extension '%(extension)s' not allowed")


class KeyPairNotFound(ResourceNotFound):
    message = _("Unable to find keypair %(keypair)s.")


class DigitalServiceNotFound(ResourceNotFound):
    message = _("A digital service %(digital_service_id)s could not be found.")


class DigitalServiceAlreadyExists(Conflict):
    message = _("A digital service with ID %(id)s already exists.")


class TrustCreateFailed(DigitalException):
    message = _("Failed to create trust for trustee %(trustee_user_id)s.")


class TrustDeleteFailed(DigitalException):
    message = _("Failed to delete trust %(trust_id)s.")


class TrusteeCreateFailed(DigitalException):
    message = _("Failed to create trustee %(username)s "
                "in domain %(domain_id)s")


class TrusteeDeleteFailed(DigitalException):
    message = _("Failed to delete trustee %(trustee_id)s")


class RegionsListFailed(DigitalException):
    message = _("Failed to list regions.")


class ServicesListFailed(DigitalException):
    message = _("Failed to list services.")


class TrusteeOrTrustToClusterFailed(DigitalException):
    message = _("Failed to create trustee or trust for Cluster: "
                "%(cluster_uuid)s")


class CertificatesToClusterFailed(DigitalException):
    message = _("Failed to create certificates for Cluster: %(cluster_uuid)s")


class FederationNotFound(ResourceNotFound):
    message = _("Federation %(federation)s could not be found.")


class FederationAlreadyExists(Conflict):
    message = _("A federation with UUID %(uuid)s already exists.")


class MemberAlreadyExists(Conflict):
    message = _("A cluster with UUID %(uuid)s is already a member of the"
                "federation %(federation_name)s.")
