# -*- coding: utf-8 -*-

from raw_sql_migrate.exceptions import RawSqlMigrateException

__all__ = (
    'BaseApi',
)


class BaseApi(object):

    engine = None
    host = None
    port = None
    name = None
    user = None
    password = None
    additional_connection_params = {}
    _connection = None
    default_port = None

    class CursorResult(object):

        ROWCOUNT = 'rowcount'
        FETCHALL = 'fetchall'

    def __init__(self, host, port, name, user, password, additional_connection_params):
        self.host = host
        self.port = port
        self.name = name
        self.user = user
        self.password = password
        self.additional_connection_params = additional_connection_params

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connection:
            self._connection.close()

    @property
    def connection(self):
        raise NotImplementedError()

    def rollback(self):
        self._connection.rollback()

    def commit(self):
        self._connection.commit()

    def execute(self, sql, params=None, return_result=None):
        if not params:
            params = {}

        result = None

        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, params)
            if return_result is None:
                result = None
            elif return_result == BaseApi.CursorResult.ROWCOUNT:
                result = cursor.rowcount
            elif return_result == BaseApi.CursorResult.FETCHALL:
                result = cursor.fetchall()
        except Exception as e:
            cursor.close()
            self.connection.close()
            raise RawSqlMigrateException(e)

        return result
