from oslo_utils import importutils


profiler_opts = importutils.try_import('osprofiler.opts')


def register_opts(conf):
    if profiler_opts:
        profiler_opts.set_defaults(conf)


def list_opts():
    return {
        profiler_opts._profiler_opt_group: profiler_opts._PROFILER_OPTS
    }