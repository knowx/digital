from oslo_config import cfg
from oslo_db import options

from digital.conf import paths


connection = 'mysql+pymysql://digital:digital@127.0.0.1/digital'

# _DEFAULT_SQL_CONNECTION = 'sqlite:///' + paths.state_path_def('digital.sqlite')

database_group = cfg.OptGroup(name='database',
                              title='Options for Digital Database')

sql_opts = [
    cfg.StrOpt('mysql_engine',
               default='InnoDB',
               help='MySQL engine to use.')
]


def register_opts(conf):
    conf.register_group(database_group)
    conf.register_opts(sql_opts, group=database_group)
    options.set_defaults(conf, connection=connection)


def list_opts():
    return {
        database_group: sql_opts
    }