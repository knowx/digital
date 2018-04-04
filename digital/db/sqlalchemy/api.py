from oslo_db.sqlalchemy import session as db_session
from oslo_log import log

from digital.db import api
import digital.conf

LOG = log.getLogger(__name__)

CONF = digital.conf.CONF

_FACADE = None


def _create_facade_lazily():
    global _FACADE
    if _FACADE is None:
        _FACADE = db_session.EngineFacade.from_config(CONF)

    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def get_backend():
    """The backend is this module itself."""
    return Connection()


class Connection(api.Connection):
    """SqlAlchemy connection."""

    def __init__(self):
        pass