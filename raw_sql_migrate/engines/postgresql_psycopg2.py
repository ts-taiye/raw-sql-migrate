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

    @property
    def connection(self):

        if not connect:
            raise Exception(u'Failed to import psycopg2, ensure you have installed it')

        if self._connection is None:
            self._connection = connect(
                database=self.name,
                user=self.user,
                password=self.password,
                port=self.port,
                host=self.host,
                **self.additional_connection_params
            )
        return self._connection

    def rollback(self):
        self.connection.rollback()

    def commit(self):
        self.connection.commit()

    def execute(self, sql, params=None, return_result=None):

        if not params:
            params = {}

        result = None

        with self.connection.cursor() as cursor:
            cursor.execute(sql, params)
            if return_result is None:
                result = None
            elif return_result == DatabaseApi.CursorResult.ROWCOUNT:
                result = cursor.rowcount
            elif return_result == DatabaseApi.CursorResult.FETCHALL:
                result = cursor.fetchall()

        return result
