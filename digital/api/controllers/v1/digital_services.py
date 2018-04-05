import pecan
import wsme
from wsme import types as wtypes

from digital.api.controllers import base
from digital.api.controllers.v1 import collection
from digital.api.controllers.v1 import types
from digital.api import expose
from digital.api import servicegroup as svcgrp_api
from digital.common import policy
from digital import objects
from digital.objects import fields


class DigitalService(base.APIBase):

    host = wtypes.StringType(min_length=1, max_length=255)
    """Name of the host """

    binary = wtypes.Enum(str, *fields.DigitalServiceBinary.ALL)
    """Name of the binary"""

    state = wtypes.Enum(str, *fields.DigitalServiceState.ALL)
    """State of the binary"""

    id = wsme.wsattr(wtypes.IntegerType(minimum=1))
    """The id for the healthcheck record """

    report_count = wsme.wsattr(wtypes.IntegerType(minimum=0))
    """The number of times the heartbeat was reported """

    disabled = wsme.wsattr(types.boolean, default=False)
    """If the service is 'disabled' administratively """

    disabled_reason = wtypes.StringType(min_length=0, max_length=255)
    """Reason for disabling """

    def __init__(self, state, **kwargs):
        super(DigitalService, self).__init__()

        self.fields = ['state']
        setattr(self, 'state', state)
        for field in objects.DigitalService.fields:
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, wtypes.Unset))


class DigitalServiceCollection(collection.Collection):

    digital_services = [DigitalService]
    """A list containing service objects"""

    def __init__(self, **kwargs):
        super(DigitalServiceCollection, self).__init__()
        self._type = 'mservices'

    @staticmethod
    def convert_db_rec_list_to_collection(servicegroup_api,
                                          rpc_msvcs, **kwargs):
        collection = DigitalServiceCollection()
        collection.mservices = []
        for p in rpc_msvcs:
            alive = servicegroup_api.service_is_up(p)
            state = 'up' if alive else 'down'
            msvc = DigitalService(state, **p.as_dict())
            collection.mservices.append(msvc)
        collection.next = collection.get_next(limit=None, url=None, **kwargs)
        return collection


class DigitalServiceController(base.Controller):
    """REST controller for digital-services."""

    def __init__(self, **kwargs):
        super(DigitalServiceController, self).__init__()
        self.servicegroup_api = svcgrp_api.ServiceGroup()

    @expose.expose(DigitalServiceCollection)
    @policy.enforce_wsgi("digital-service")
    def get_all(self):
        """Retrieve a list of digital-services.

        """
        msvcs = objects.DigitalService.list(pecan.request.context,
                                            limit=None,
                                            marker=None,
                                            sort_key='id',
                                            sort_dir='asc')

        return DigitalServiceCollection.convert_db_rec_list_to_collection(
            self.servicegroup_api, msvcs)
