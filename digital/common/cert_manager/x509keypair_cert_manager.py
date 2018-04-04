from digital.common.cert_manager import cert_manager
from digital import objects


class Cert(cert_manager.Cert):
    """Representation of a Cert for Digital DB storage."""
    def __init__(self, certificate, private_key, intermediates=None,
                 private_key_passphrase=None):
        self.certificate = certificate
        self.intermediates = intermediates
        self.private_key = private_key
        self.private_key_passphrase = private_key_passphrase

    def get_certificate(self):
        return self.certificate

    def get_intermediates(self):
        return self.intermediates

    def get_private_key(self):
        return self.private_key

    def get_private_key_passphrase(self):
        return self.private_key_passphrase


class CertManager(cert_manager.CertManager):
    """Cert Manager Interface that stores data locally in Digital db.

    """

    @staticmethod
    def store_cert(certificate, private_key, intermediates=None,
                   private_key_passphrase=None, context=None, **kwargs):
        """Stores (i.e., registers) a cert with the cert manager.

        This method stores the specified cert to x509keypair model and returns
        a UUID that can be used to retrieve it.

        :param certificate: PEM encoded TLS certificate
        :param private_key: private key for the supplied certificate
        :param intermediates: ordered and concatenated intermediate certs
        :param private_key_passphrase: optional passphrase for the supplied key

        :returns: the UUID of the stored cert
        """
        x509keypair = {'certificate': certificate, 'private_key': private_key,
                       'private_key_passphrase': private_key_passphrase,
                       'intermediates': intermediates,
                       'project_id': context.project_id,
                       'user_id': context.user_id}
        x509keypair_obj = objects.X509KeyPair(context, **x509keypair)
        x509keypair_obj.create()
        return x509keypair_obj.uuid

    @staticmethod
    def get_cert(cert_ref, context=None, **kwargs):
        """Retrieves the specified cert.

        :param cert_ref: the UUID of the cert to retrieve

        :return: digital.common.cert_manager.cert_manager.Cert
                 representation of the certificate data
        """
        cert_data = dict()
        x509keypair_obj = objects.X509KeyPair.get_by_uuid(context, cert_ref)
        cert_data['certificate'] = x509keypair_obj.certificate
        cert_data['private_key'] = x509keypair_obj.private_key
        cert_data['private_key_passphrase'] = \
            x509keypair_obj.private_key_passphrase
        cert_data['intermediates'] = x509keypair_obj.intermediates
        return Cert(**cert_data)

    @staticmethod
    def delete_cert(cert_ref, context=None, **kwargs):
        """Deletes the specified cert.

        :param cert_ref: the UUID of the cert to delete
        """
        x509keypair_obj = objects.X509KeyPair.get_by_uuid(context, cert_ref)
        x509keypair_obj.destroy()
