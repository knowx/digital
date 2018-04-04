import os
import sys

from oslo_concurrency import processutils
from oslo_log import log as logging
from oslo_reports import guru_meditation_report as gmr

from werkzeug import serving

from digital.api import app as api_app
from digital.common import profiler
from digital.common import service
from digital import conf
from digital.i18n import _
from digital.objects import base
from digital import version

CONF = conf.CONF
LOG = logging.getLogger(__name__)


def _get_ssl_configs(use_ssl):
    if use_ssl:
        cert_file = CONF.api.ssl_cert_file
        key_file = CONF.api.ssl_key_file

        if cert_file and not os.path.exists(cert_file):
            raise RuntimeError(
                _("Unable to find cert_file : %s") % cert_file)

        if key_file and not os.path.exists(key_file):
            raise RuntimeError(
                _("Unable to find key_file : %s") % key_file)

        return cert_file, key_file
    else:
        return None


def main():
    service.prepare_service(sys.argv)

    gmr.TextGuruMeditation.setup_autorun(version)
    base.DigitalObject.indirection_api = base.DigitalObjectIndirectionAPI()
    
    app = api_app.load_app()

    # Setup OSprofiler for WSGI service
    profiler.setup('digital-api', CONF.host)

    # SSL configuration
    use_ssl = CONF.api.enabled_ssl

    # Create the WSGI server and start it
    host, port = CONF.api.host, CONF.api.port

    LOG.info('Starting server in PID %s', os.getpid())
    LOG.debug("Configuration:")
    CONF.log_opt_values(LOG, logging.DEBUG)

    LOG.info('Serving on %(proto)s://%(host)s:%(port)s',
             dict(proto="https" if use_ssl else "http", host=host, port=port))

    workers = CONF.api.workers
    if not workers:
        workers = processutils.get_worker_count()
    LOG.info('Server will handle each request in a new process up to'
             ' %s concurrent processes', workers)
    serving.run_simple(host, port, app, processes=workers,
                       ssl_context=_get_ssl_configs(use_ssl))
