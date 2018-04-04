
__all__ = [
    'init',
    'cleanup',
    'set_defaults',
    'add_extra_exmods',
    'clear_extra_exmods',
    'get_allowed_exmods',
    'RequestContextSerializer',
    'get_client',
    'get_server',
    'get_notifier',
]

import socket


import oslo_messaging as messaging
from oslo_messaging.rpc import dispatcher
from oslo_serialization import jsonutils
from oslo_utils import importutils

from digital.common import context as digital_context
from digital.common import exception
from digital import conf

profiler = importutils.try_import("osprofiler.profiler")

CONF = conf.CONF
TRANSPORT = None
NOTIFIER = None

ALLOWED_EXMODS = [
    exception.__name__,
]
EXTRA_EXMODS = []


def init(conf):
    global TRANSPORT, NOTIFIER
    exmods = get_allowed_exmods()
    TRANSPORT = messaging.get_rpc_transport(conf,
                                            allowed_remote_exmods=exmods)
    serializer = RequestContextSerializer(JsonPayloadSerializer())
    NOTIFIER = messaging.Notifier(TRANSPORT, serializer=serializer)


def cleanup():
    global TRANSPORT, NOTIFIER
    assert TRANSPORT is not None
    assert NOTIFIER is not None
    TRANSPORT.cleanup()
    TRANSPORT = NOTIFIER = None


def set_defaults(control_exchange):
    messaging.set_transport_defaults(control_exchange)


def add_extra_exmods(*args):
    EXTRA_EXMODS.extend(args)


def clear_extra_exmods():
    del EXTRA_EXMODS[:]


def get_allowed_exmods():
    return ALLOWED_EXMODS + EXTRA_EXMODS


class JsonPayloadSerializer(messaging.NoOpSerializer):
    @staticmethod
    def serialize_entity(context, entity):
        return jsonutils.to_primitive(entity, convert_instances=True)


class RequestContextSerializer(messaging.Serializer):

    def __init__(self, base):
        self._base = base

    def serialize_entity(self, context, entity):
        if not self._base:
            return entity
        return self._base.serialize_entity(context, entity)

    def deserialize_entity(self, context, entity):
        if not self._base:
            return entity
        return self._base.deserialize_entity(context, entity)

    def serialize_context(self, context):
        return context.to_dict()

    def deserialize_context(self, context):
        return digital_context.RequestContext.from_dict(context)


class ProfilerRequestContextSerializer(RequestContextSerializer):
    def serialize_context(self, context):
        _context = super(ProfilerRequestContextSerializer,
                         self).serialize_context(context)

        prof = profiler.get()
        if prof:
            trace_info = {
                "hmac_key": prof.hmac_key,
                "base_id": prof.get_base_id(),
                "parent_id": prof.get_id()
            }
            _context.update({"trace_info": trace_info})

        return _context

    def deserialize_context(self, context):
        trace_info = context.pop("trace_info", None)
        if trace_info:
            profiler.init(**trace_info)

        return super(ProfilerRequestContextSerializer,
                     self).deserialize_context(context)


def get_transport_url(url_str=None):
    return messaging.TransportURL.parse(CONF, url_str)


def get_client(target, version_cap=None, serializer=None, timeout=None):
    assert TRANSPORT is not None
    if profiler:
        serializer = ProfilerRequestContextSerializer(serializer)
    else:
        serializer = RequestContextSerializer(serializer)

    return messaging.RPCClient(TRANSPORT,
                               target,
                               version_cap=version_cap,
                               serializer=serializer,
                               timeout=timeout)


def get_server(target, endpoints, serializer=None):
    assert TRANSPORT is not None
    access_policy = dispatcher.DefaultRPCAccessPolicy
    if profiler:
        serializer = ProfilerRequestContextSerializer(serializer)
    else:
        serializer = RequestContextSerializer(serializer)

    return messaging.get_rpc_server(TRANSPORT,
                                    target,
                                    endpoints,
                                    executor='eventlet',
                                    serializer=serializer,
                                    access_policy=access_policy)


def get_notifier(service='container-infra', host=None, publisher_id=None):
    assert NOTIFIER is not None
    myhost = CONF.host
    if myhost is None:
        myhost = socket.getfqdn()
    if not publisher_id:
        publisher_id = "%s.%s" % (service, host or myhost)
    return NOTIFIER.prepare(publisher_id=publisher_id)
