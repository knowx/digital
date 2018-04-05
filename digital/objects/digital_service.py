from oslo_versionedobjects import fields

from digital.db import api as dbapi
from digital.objects import base


@base.DigitalObjectRegistry.register
class DigitalService(base.DigitalPersistentObject, base.DigitalObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    dbapi = dbapi.get_instance()

    fields = {
        'id': fields.IntegerField(),
        'host': fields.StringField(nullable=True),
        'binary': fields.StringField(nullable=True),
        'disabled': fields.BooleanField(),
        'disabled_reason': fields.StringField(nullable=True),
        'last_seen_up': fields.DateTimeField(nullable=True),
        'forced_down': fields.BooleanField(),
        'report_count': fields.IntegerField(),
    }

    @staticmethod
    def _from_db_object(digital_service, db_digital_service):
        """Converts a database entity to a formal object."""
        for field in digital_service.fields:
            setattr(digital_service, field, db_digital_service[field])

        digital_service.obj_reset_changes()
        return digital_service

    @staticmethod
    def _from_db_object_list(db_objects, cls, context):
        """Converts a list of database entities to a list of formal objects."""
        return [DigitalService._from_db_object(cls(context), obj)
                for obj in db_objects]

    @base.remotable_classmethod
    def get_by_host_and_binary(cls, context, host, binary):
        """Find a digital_service based on its hostname and binary.

        :param host: The host on which the binary is running.
        :param binary: The name of the binary.
        :param context: Security context.
        :returns: a :class:`DigitalService` object.
        """
        db_digital_service = cls.dbapi.get_digital_service_by_host_and_binary(
            host, binary)
        if db_digital_service is None:
            return None
        digital_service = DigitalService._from_db_object(
            cls(context), db_digital_service)
        return digital_service

    @base.remotable_classmethod
    def list(cls, context, limit=None, marker=None,
             sort_key=None, sort_dir=None):
        """Return a list of DigitalService objects.

        :param context: Security context.
        :param limit: maximum number of resources to return in a single result.
        :param marker: pagination marker for large data sets.
        :param sort_key: column to sort results by.
        :param sort_dir: direction to sort. "asc" or "desc".
        :returns: a list of :class:`DigitalService` object.

        """
        db_digital_services = cls.dbapi.get_digital_service_list(
            limit=limit, marker=marker, sort_key=sort_key,
            sort_dir=sort_dir)
        return DigitalService._from_db_object_list(db_digital_services, cls,
                                                  context)

    @base.remotable
    def create(self, context=None):
        """Create a DigitalService record in the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: DigitalService(context)
        """
        values = self.obj_get_changes()
        db_digital_service = self.dbapi.create_digital_service(values)
        self._from_db_object(self, db_digital_service)

    @base.remotable
    def destroy(self, context=None):
        """Delete the DigitalService from the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: DigitalService(context)
        """
        self.dbapi.destroy_digital_service(self.id)
        self.obj_reset_changes()

    @base.remotable
    def save(self, context=None):
        """Save updates to this DigitalService.

        Updates will be made column by column based on the result
        of self.what_changed().

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: DigitalService(context)
        """
        updates = self.obj_get_changes()
        self.dbapi.update_digital_service(self.id, updates)
        self.obj_reset_changes()

    @base.remotable
    def report_state_up(self, context=None):
        """Touching the digital_service record to show aliveness.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: DigitalService(context)
        """
        self.report_count += 1
        self.save()
