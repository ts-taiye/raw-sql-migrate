# -*- coding: utf-8 -*-

try:
    from psycopg2 import connect
except ImportError:
    connect = None

from raw_sql_migrate.engines.base import BaseApi

__all__ = (
    'DatabaseApi',
)


class DatabaseApi(BaseApi):

    engine = __name__
    default_port = 5432

    @property
    def connection(self):

        if not connect:
            raise Exception('Failed to import psycopg2, ensure you have installed it')

        if self._connection is None:
            self._connection = connect(
                database=self.name,
                user=self.user,
                password=self.password,
                port=self.port if self.port else self.default_port,
                host=self.host,
                **self.additional_connection_params
            )
        return self._connection
