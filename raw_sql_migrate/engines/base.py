# -*- coding: utf-8 -*-

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
        raise NotImplementedError()

    def commit(self):
        raise NotImplementedError()

    def execute(self, sql, params=None, return_result=None, commit=True):
        raise NotImplementedError()
