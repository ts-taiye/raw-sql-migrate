
try:
    from MySQLdb import connect
except ImportError:
    connect = None

from raw_sql_migrate.engines.base import BaseApi

__all__ = (
    'DatabaseApi',
)


class DatabaseApi(BaseApi):

    engine = __name__
    default_port = 3306

    @property
    def connection(self):

        if not connect:
            raise Exception('Failed to import MySQLdb, ensure you have installed MySQLdb-python package')

        if self._connection is None:
            port = self.port if self.port else self.default_port
            self._connection = connect(
                db=self.name,
                user=self.user,
                passwd=self.password,
                port=port,
                host=self.host,
                **self.additional_connection_params
            )
        return self._connection
