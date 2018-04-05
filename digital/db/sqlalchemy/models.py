import json

from oslo_db.sqlalchemy import models
from oslo_db.sqlalchemy.types import String
import six.moves.urllib.parse as urlparse
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer
from sqlalchemy import schema
from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator, TEXT
from sqlalchemy.dialects.mysql import TEXT as mysql_TEXT
from sqlalchemy.dialects.mysql import TINYTEXT

from digital import conf

CONF = conf.CONF


def table_args():
    engine_name = urlparse.urlparse(CONF.database.connection).scheme
    if engine_name == 'mysql':
        return {'mysql_engine': CONF.database.mysql_engine,
                'mysql_charset': "utf8"}
    return None


class JsonEncodedType(TypeDecorator):
    """Abstract base type serialized as json-encoded string in db."""
    type = None
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            # Save default value according to current type to keep the
            # interface the consistent.
            value = self.type()
        elif not isinstance(value, self.type):
            raise TypeError("%(class)s supposes to store "
                            "%(type)s objects, but %(value)s "
                            "given" % {'class': self.__class__.__name__,
                                       'type': self.type.__name__,
                                       'value': type(value).__name__})
        serialized_value = json.dumps(value)
        return serialized_value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class JSONEncodedDict(JsonEncodedType):
    """Represents dict serialized as json-encoded string in db."""
    type = dict


class JSONEncodedList(JsonEncodedType):
    """Represents list serialized as json-encoded string in db."""
    type = list


class DigitalBase(models.TimestampMixin,
                  models.ModelBase):

    metadata = None

    def as_dict(self):
        d = {}
        for c in self.__table__.columns:
            d[c.name] = self[c.name]
        return d

    def save(self, session=None):
        import digital.db.sqlalchemy.api as db_api

        if session is None:
            session = db_api.get_session()

        super(DigitalBase, self).save(session)


Base = declarative_base(cls=DigitalBase)
    
    
class DigitalService(Base):
    """Represents health status of various digital services"""
    __tablename__ = 'digital_service'
    __table_args__ = (
        schema.UniqueConstraint("host", "binary",
                                name="uniq_digital_service0host0binary"),
        table_args()
    )

    id = Column(Integer, primary_key=True)
    host = Column(String(255))
    binary = Column(String(255))
    disabled = Column(Boolean, default=False)
    disabled_reason = Column(String(255))
    last_seen_up = Column(DateTime, nullable=True)
    forced_down = Column(Boolean, default=False)
    report_count = Column(Integer, nullable=False, default=0)