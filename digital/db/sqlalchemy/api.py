from oslo_db import exception as db_exc
from oslo_db.sqlalchemy import session as db_session
from oslo_db.sqlalchemy import utils as db_utils
from oslo_log import log
from oslo_utils import importutils
from oslo_utils import strutils
from oslo_utils import timeutils
from oslo_utils import uuidutils
from sqlalchemy.orm.exc import NoResultFound

from digital.common import clients
from digital.common import context as request_context
from digital.common import exception
from digital import conf
from digital.db import api
from digital.db.sqlalchemy import models
from digital.i18n import _

profiler_sqlalchemy = importutils.try_import('osprofiler.sqlalchemy')

CONF = conf.CONF

LOG = log.getLogger(__name__)

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

def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """

    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)
    return query


def add_identity_filter(query, value):
    """Adds an identity filter to a query.

    Filters results by ID, if supplied value is a valid integer.
    Otherwise attempts to filter results by UUID.

    :param query: Initial query to add filter to.
    :param value: Value for filtering results by.
    :return: Modified query.
    """
    if strutils.is_int_like(value):
        return query.filter_by(id=value)
    elif uuidutils.is_uuid_like(value):
        return query.filter_by(uuid=value)
    else:
        raise exception.InvalidIdentity(identity=value)


def _paginate_query(model, limit=None, marker=None, sort_key=None,
                    sort_dir=None, query=None):
    if not query:
        query = model_query(model)
    sort_keys = ['id']
    if sort_key and sort_key not in sort_keys:
        sort_keys.insert(0, sort_key)
    try:
        query = db_utils.paginate_query(query, model, limit, sort_keys,
                                        marker=marker, sort_dir=sort_dir)
    except db_exc.InvalidSortKey:
        raise exception.InvalidParameterValue(
            _('The sort_key value "%(key)s" is an invalid field for sorting')
            % {'key': sort_key})
    return query.all()


class Connection(api.Connection):
    """SqlAlchemy connection."""

    def __init__(self):
        pass

    def _add_tenant_filters(self, context, query):
        if context.is_admin and context.all_tenants:
            return query

        admin_context = request_context.make_admin_context(all_tenants=True)
        osc = clients.OpenStackClients(admin_context)
        kst = osc.keystone()

        # User in a regular project (not in the trustee domain)
        if context.project_id and context.domain_id != kst.trustee_domain_id:
            query = query.filter_by(project_id=context.project_id)
        # Match project ID component in trustee user's user name against
        # cluster's project_id to associate per-cluster trustee users who have
        # no project information with the project their clusters/cluster models
        # reside in. This is equivalent to the project filtering above.
        elif context.domain_id == kst.trustee_domain_id:
            user_name = kst.client.users.get(context.user_id).name
            user_project = user_name.split('_', 2)[1]
            query = query.filter_by(project_id=user_project)
        else:
            query = query.filter_by(user_id=context.user_id)

        return query

    def get_digital_service_by_host_and_binary(self, host, binary):
        query = model_query(models.DigitalService)
        query = query.filter_by(host=host, binary=binary)
        try:
            return query.one()
        except NoResultFound:
            return None

    def get_digital_service_list(self, disabled=None, limit=None,
                                marker=None, sort_key=None, sort_dir=None
                                ):
        query = model_query(models.DigitalService)
        if disabled:
            query = query.filter_by(disabled=disabled)

        return _paginate_query(models.DigitalService, limit, marker,
                               sort_key, sort_dir, query)

    def create_digital_service(self, values):
        digital_service = models.DigitalService()
        digital_service.update(values)
        try:
            digital_service.save()
        except db_exc.DBDuplicateEntry:
            host = values["host"]
            binary = values["binary"]
            LOG.warning("Digital service with same host:%(host)s and"
                        " binary:%(binary)s had been saved into DB",
                        {'host': host, 'binary': binary})
            query = model_query(models.DigitalService)
            query = query.filter_by(host=host, binary=binary)
            return query.one()
        return digital_service

    def update_digital_service(self, digital_service_id, values):
        session = get_session()
        ref = None
        with session.begin():
            query = model_query(models.DigitalService, session=session)
            query = add_identity_filter(query, digital_service_id)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.DigitalServiceNotFound(
                    digital_service_id=digital_service_id)

            if 'report_count' in values:
                if values['report_count'] > ref.report_count:
                    ref.last_seen_up = timeutils.utcnow()

            ref.update(values)
        return ref

    def destroy_digital_service(self, digital_service_id):
        session = get_session()
        with session.begin():
            query = model_query(models.DigitalService, session=session)
            query = add_identity_filter(query, digital_service_id)
            count = query.delete()
            if count != 1:
                raise exception.DigitalServiceNotFound(
                    digital_service_id=digital_service_id)