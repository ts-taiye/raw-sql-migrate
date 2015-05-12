# -*- coding: utf-8 -*-

from psycopg2 import connect

__all__ = (
    'DatabaseApi',
)


class DatabaseApi(object):

    host = None
    port = None
    name = None
    user = None
    password = None
    _connection = None

    def __init__(self, host, port, name, user, password):
        self.host = host
        self.port = port
        self.name = name
        self.user = user
        self.password = password

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connection:
            self._connection.close()

    @property
    def connection(self):
        if self._connection is None:
            self._connection = connect(
                database=self.name,
                user=self.user,
                password=self.password,
                port=self.port,
                host=self.host
            )
        return self._connection

    def execute(self, sql, params=None, return_result=None, commit=True):

        if not params:
            params = {}

        result = None

        with self.connection.cursor() as cursor:
            cursor.execute(sql, params)
            if not return_result:
                result = None
            elif return_result == 'rowcount':
                result = cursor.rowcount
            elif return_result == 'fetchall':
                result = cursor.fetchall()

            if commit:
                self.connection.commit()

        return result
