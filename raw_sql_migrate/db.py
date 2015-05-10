# -*- coding: utf-8 -*-

from psycopg2 import connect, ProgrammingError

from raw_sql_migrate import config as yaml_config

__all__ = (
    'execute',
    'migration_history_exists',
    'get_latest_migration_number',
    'create_history_table',
    'write_migration_history',
    'delete_migration_history',
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


def migration_history_exists(database_api, config=None):

    sql = '''
    SELECT *
    FROM information_schema.tables
    WHERE table_name=%(history_table_name)s
    '''
    try:
        result = database_api.execute(
            sql,
            params={'history_table_name': config.history_table_name},
            return_result='rowcount',
            commit=False
        )
    except ProgrammingError:
        result = None

    return True if result else False


def get_latest_migration_number(database_api, package, config=None):
    result = 0

    if not config:
        config = yaml_config

    sql = '''
        SELECT name
        FROM %s
        WHERE package = %%s
        ORDER BY id DESC LIMIT 1;
    ''' % config.history_table_name
    query_params = (package, )

    rows = database_api.execute(sql, params=query_params, return_result='fetchall', commit=False)
    if rows:
        name = rows[0][0]
        result = int(name.split('_')[0].strip('0'))

    return result


def create_history_table(database_api, config=None):

    if not config:
        config = yaml_config

    sql = '''
        CREATE TABLE %s (
            id SERIAL PRIMARY KEY,
            package VARCHAR(200) NOT NULL,
            name VARCHAR(200) NOT NULL,
            processed_at  TIMESTAMP default current_timestamp
        );
    ''' % config.history_table_name
    database_api.execute(sql, params=(config.history_table_name, ), return_result=None, commit=True)


def write_migration_history(database_api, name, package, config=None):

    if not config:
        config = yaml_config

    sql = '''
        INSERT INTO %s(name, package)
        VALUES (%%s, %%s);
    ''' % config.history_table_name
    database_api.execute(sql, params=(name, package, ), return_result=None, commit=True)


def delete_migration_history(database_api, name, package, config=None):

    if not config:
        config = yaml_config

    sql = '''
        DELETE FROM %s
        WHERE name=%%s and package=%%s
    ''' % config.history_table_name
    database_api.execute(sql, params=(name, package, ), return_result=None, commit=True)
