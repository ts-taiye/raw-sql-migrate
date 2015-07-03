# -*- coding: utf-8 -*-

__all__ = (
    'database_api_storage'
)

class DatabaseApiStorage(object):

    _database_api = None

    @property
    def database_api(self):
        return self._database_api

    def set_database_api(self, database_api_instance):
        self._database_api = database_api_instance

database_api_storage = DatabaseApiStorage()
