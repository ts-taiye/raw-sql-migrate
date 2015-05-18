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
    _connection = None

    class CursorResult(object):

        ROWCOUNT = 'rowcount'
        FETCHALL = 'fetchall'

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
        raise NotImplementedError()

    def execute(self, sql, params=None, return_result=None, commit=True):
        raise NotImplementedError()
