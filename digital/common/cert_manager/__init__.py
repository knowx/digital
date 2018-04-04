from stevedore import driver

import digital.conf

CONF = digital.conf.CONF

_CERT_MANAGER_PLUGIN = None


def get_backend():
    global _CERT_MANAGER_PLUGIN
    if not _CERT_MANAGER_PLUGIN:
        _CERT_MANAGER_PLUGIN = driver.DriverManager(
            "digital.cert_manager.backend",
            CONF.certificates.cert_manager_type).driver
    return _CERT_MANAGER_PLUGIN
