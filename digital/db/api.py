import abc

import six

from oslo_config import cfg
from oslo_db import api as db_api

_BACKEND_MAPPING = {'sqlalchemy': 'digital.db.sqlalchemy.api'}
IMPL = db_api.DBAPI.from_config(cfg.CONF, backend_mapping=_BACKEND_MAPPING, lazy=True)


def get_instance():
    """Return a DB API instance."""
    return IMPL


@six.add_metaclass(abc.ABCMeta)
class Connection(object):
    """Base class for storage system connections."""

    @abc.abstractmethod
    def __init__(self):
        """Constructor."""

    @abc.abstractmethod
    def destroy_digital_service(self, digital_service_id):
        """Destroys a digital_service record.

        :param digital_service_id: The id of a digital_service.
        """

    @abc.abstractmethod
    def update_digital_service(self, digital_service_id, values):
        """Update properties of a digital_service.

        :param digital_service_id: The id of a digital_service record.
        """

    @abc.abstractmethod
    def get_digital_service_by_host_and_binary(self, host, binary):
        """Return a digital_service record.

        :param host: The host where the binary is located.
        :param binary: The name of the binary.
        :returns: A digital_service record.
        """

    @abc.abstractmethod
    def create_digital_service(self, values):
        """Create a new digital_service record.

        :param values: A dict containing several items used to identify
                       and define the digital_service record.
        :returns: A digital_service record.
        """

    @abc.abstractmethod
    def get_digital_service_list(self, disabled=None, limit=None,
                                marker=None, sort_key=None, sort_dir=None):
        """Get matching digital_service records.

        Return a list of the specified columns for all digital_services
        those match the specified filters.

        :param disabled: Filters disbaled services. Defaults to None.
        :param limit: Maximum number of digital_services to return.
        :param marker: the last item of the previous page; we return the next
                       result set.
        :param sort_key: Attribute by which results should be sorted.
        :param sort_dir: direction in which results should be sorted.
                         (asc, desc)
        :returns: A list of tuples of the specified columns.
        """
