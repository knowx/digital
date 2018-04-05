from oslo_utils import timeutils

from digital import conf
from digital.objects import digital_service

CONF = conf.CONF


class ServiceGroup(object):
    def __init__(self):
        self.service_down_time = CONF.service_down_time

    def service_is_up(self, member):
        if not isinstance(member, digital_service.DigitalService):
            raise TypeError
        if member.forced_down:
            return False

        last_heartbeat = (member.last_seen_up or
                          member.updated_at or member.created_at)
        now = timeutils.utcnow(True)
        elapsed = timeutils.delta_seconds(last_heartbeat, now)
        is_up = abs(elapsed) <= self.service_down_time
        return is_up
