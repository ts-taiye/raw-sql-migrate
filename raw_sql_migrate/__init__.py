# -*- coding: utf-8 -*-

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class Config(object):

    host = None
    port = None
    name = None
    user = None
    password = None
    history_table_name = 'migration_history'

    def init_from_file(self):
        config_name = 'raw_sql_migrate.yaml'
        with open(config_name, 'r') as file_stream:
            config_data = load(file_stream, Loader)
        database_settings = config_data['database']
        self.host = database_settings['host']
        self.port = database_settings['port']
        self.name = database_settings['name']
        self.user = database_settings['user']
        self.password = database_settings['password']
        self.history_table_name = config_data['history_table_name']

config = Config()
config.init_from_file()

