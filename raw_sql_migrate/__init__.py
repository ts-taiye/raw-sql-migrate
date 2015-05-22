# -*- coding: utf-8 -*-

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class Config(object):

    engine = None
    host = None
    port = None
    name = None
    user = None
    password = None
    additional_connection_params = {}
    history_table_name = 'migration_history'
    general_connection_params = set(('engine', 'host', 'port', 'name', 'user', 'password', ))

    def __init__(self, database=None, history_table_name=None):
        if database and type(database) == dict:
            self.engine = database.get('engine')
            self.host = database.get('host')
            self.port = database.get('port')
            self.name = database.get('name')
            self.user = database.get('user')
            self.password = database.get('password')
            additional_connection_params = dict(
                [(key, database[key]) for key in (set(database.keys()) - set(self.general_connection_params))]
            )
            if additional_connection_params:
                self.additional_connection_params = additional_connection_params

        if history_table_name:
            self.history_table_name = history_table_name

    def init_from_file(self, path_to_config=None):
        if not path_to_config:
            path_to_config = 'raw_sql_migrate.yaml'
        with open(path_to_config, 'r') as file_stream:
            config_data = load(file_stream, Loader)
        database_settings = config_data.get('database')
        history_table_name = config_data.get('history_table_name')
        self.__init__(database_settings, history_table_name)
        return self

config = Config()
try:
    config.init_from_file()
except IOError:
    pass
