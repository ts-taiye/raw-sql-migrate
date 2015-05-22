
try:
    from MySQLdb import connect
except ImportError:
    connect = None

from raw_sql_migrate.engines.base import BaseApi
from raw_sql_migrate.exceptions import RawSqlMigrateException

__all__ = (
    'DatabaseApi',
)


class DatabaseApi(BaseApi):

    DEFAULT_MY_SQL_PORT = 3306

    @property
    def connection(self):

        if not connect:
            raise Exception(u'Failed to import MySQLdb, ensure you have installed MySQLdb-python package')

        if self._connection is None:
            port = self.port if self.port else self.DEFAULT_MY_SQL_PORT
            self._connection = connect(
                db=self.name,
                user=self.user,
                passwd=self.password,
                port=port,
                host=self.host,
                **self.additional_connection_params
            )
        return self._connection

    def execute(self, sql, params=None, return_result=None, commit=True):

        if not params:
            params = {}

        result = None

        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, params)
            if return_result is None:
                result = None
            elif return_result == DatabaseApi.CursorResult.ROWCOUNT:
                result = cursor.rowcount
            elif return_result == DatabaseApi.CursorResult.FETCHALL:
                result = cursor.fetchall()
        except Exception as e:
            cursor.close()
            self.connection.close()
            raise RawSqlMigrateException(e)
        finally:
            if commit:
                self.connection.commit()

        return result
