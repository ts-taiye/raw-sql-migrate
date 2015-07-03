# -*- coding: utf-8 -*-

__all__ = (
    'database_api_storage'
)

class DatabaseApiStorage(object):

    _database_api = None

    def set_database_api(self, database_api_instance):
        self._database_api = database_api_instance

    def __getattr__(self, item):
        return self._database_api and getattr(self._database_api, item)

database_api = DatabaseApiStorage()
