import threading
import pbr.version


__version__ = pbr.version.VersionInfo(
    'digital').version_string()

TLS = threading.local()
