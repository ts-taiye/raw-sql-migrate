# -*- coding: utf-8 -*-

import os
import sys

from importlib import import_module


class ConfigNotFoundException(Exception):
    pass


class Config(object):

    engine = None
    host = None
    port = None
    name = None
    user = None
    password = None
    additional_connection_params = {}
    packages = []
    history_table_name = 'migration_history'
    general_connection_params = set(('engine', 'host', 'port', 'name', 'user', 'password', ))

    def __init__(self, database=None, history_table_name=None, packages=None):
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

        if packages:
            self.packages = packages

        if history_table_name:
            self.history_table_name = history_table_name

        self.config_type_handlers = {
            '.py': self._import_from_python_file,
            '.yaml': self._import_from_yaml_file,
        }

    def _import_from_python_file(self, path_to_config=None):
        path_to_config = path_to_config or 'rsm'
        sys.path.append(os.getcwd())

        try:
            module = import_module(path_to_config)
        except ImportError:
            return None

        try:
            config_data = getattr(module, 'RSM_CONFIG')
            return config_data
        except AttributeError:
            return None

    def _import_from_yaml_file(self, path_to_config=None):
        path_to_config = path_to_config or 'rsm.yaml'

        if not os.path.exists(path_to_config):
            return None

        try:
            from yaml import load
        except ImportError:
            sys.stdout.write('Found config on path %s, but PyYAML is not installed' % path_to_config)
            return None

        with open(path_to_config, 'r') as file_stream:
            config_data = load(file_stream)

        return config_data

    def init_from_file(self, path_to_config=None):
        if not path_to_config:
            config_data = None
            for handler in self.config_type_handlers.values():
                config_data = handler()
                if config_data:
                    break

            if not config_data:
                raise ConfigNotFoundException('Neither .py nor .yaml config is not found')
        else:
            config_type = '.yaml' if path_to_config.endswith('.yaml') else '.py'
            if config_type not in self.config_type_handlers:
                raise ConfigNotFoundException('Strange config type - %s' % config_type)

            config_data = self.config_type_handlers[config_type](path_to_config)

            if not config_data:
                raise ConfigNotFoundException('Cannot read config %s' % path_to_config)

        database_settings = config_data.get('database')
        history_table_name = config_data.get('history_table_name')
        packages = config_data.get('packages')
        self.__init__(database_settings, history_table_name, packages)


class ConfigStorage(object):

    _config = None

    def set_config_instance(self, config_instance):
        self._config = config_instance

    def __getattr__(self, item):
        return self._config and getattr(self._config, item)

rsm_config = ConfigStorage()
