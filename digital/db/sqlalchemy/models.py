import six.moves.urllib.parse as urlparse

from sqlalchemy import schema
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer

from oslo_db.sqlalchemy import models
from oslo_db.sqlalchemy.types import String

import digital.conf

CONF = digital.conf.CONF


def table_args():
    engine_name = urlparse.urlparse(CONF.database.connection).scheme
    if engine_name == 'mysql':
        return {'mysql_engine': CONF.database.mysql_engine,
                'mysql_charset': "utf8"}
    return None


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


class Thing(Base):

    __tablename__ = 'thing'
    __table_args__ = (
        schema.UniqueConstraint('uuid', name='uniq_thing0uuid'),
        table_args()
    )
    id = Column(Integer, primary_key=True)
    project_id = Column(String(255))
    user_id = Column(String(255))
    uuid = Column(String(36))
    name = Column(String(255))