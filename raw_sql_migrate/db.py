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


def execute(sql, params=None, return_result=None, commit=False, config=None):

    if not config:
        config = yaml_config

    if not params:
        params = {}

    result = None

    with connect(
        database=config.name,
        user=config.name,
        password=config.password,
        port=config.port,
        host=config.host,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            if not return_result:
                result = None
            elif return_result == 'rowcount':
                result = cursor.rowcount
            elif return_result == 'fetchall':
                result = cursor.fetchall()

            if commit:
                connection.commit()
    return result


def migration_history_exists(config=None):

    if not config:
        config = yaml_config

    sql = '''
    SELECT *
    FROM information_schema.tables
    WHERE table_name=%(history_table_name)s
    '''
    try:
        result = execute(
            sql,
            params={'history_table_name': config.history_table_name},
            return_result='rowcount',
            commit=False,
            config=config
        )
    except ProgrammingError:
        result = None

    return True if result else False


def get_latest_migration_number(package, config=None):
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

    rows = execute(sql, params=query_params, return_result='fetchall', commit=False, config=config)
    if rows:
        name = rows[0][0]
        result = int(name.split('_')[0].strip('0'))

    return result


def create_history_table(config=None):

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
    execute(sql, params=(config.history_table_name, ), return_result=None, commit=True, config=config)


def write_migration_history(name, package, config=None):

    if not config:
        config = yaml_config

    sql = '''
        INSERT INTO %s(name, package)
        VALUES (%%s, %%s);
    ''' % config.history_table_name
    execute(sql, params=(name, package, ), return_result=None, commit=True, config=config)


def delete_migration_history(name, package, config=None):

    if not config:
        config = yaml_config

    sql = '''
        DELETE FROM %s
        WHERE name=%%s and package=%%s
    ''' % config.history_table_name
    execute(sql, params=(name, package, ), return_result=None, commit=True, config=config)
