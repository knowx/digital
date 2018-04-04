from stevedore import driver

from digital import conf

CONF = conf.CONF
_IMPL = None


def get_backend():
    global _IMPL
    if not _IMPL:
        _IMPL = driver.DriverManager("digital.database.migration_backend",
                                     "sqlalchemy").driver
    return _IMPL


def upgrade(version=None):
    """Migrate the database to `version` or the most recent version."""
    return get_backend().upgrade(version)


def version():
    return get_backend().version()


def stamp(version):
    return get_backend().stamp(version)


def revision(message, autogenerate):
    return get_backend().revision(message, autogenerate)
