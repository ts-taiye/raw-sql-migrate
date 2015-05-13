# -*- coding: utf-8 -*-

import os

from importlib import import_module
from psycopg2 import ProgrammingError

__all__ = (
    'prepare_package_migration_directory',
    'get_package_migrations_directory',
    'get_migration_python_path_and_name',
    'MIGRATION_NAME_TEMPLATE',
    'MIGRATION_TEMPLATE',
    'DatabaseHelper',
)

MIGRATION_NAME_TEMPLATE = '%04d'
MIGRATION_TEMPLATE = """# encoding: utf-8


def forward(database_api):
    pass


def backward(database_api):
    pass

"""
INIT_FILE_TEMPLATE = """# encoding: utf-8

"""
DIGITS_IN_MIGRATION_NUMBER = 4


def get_package_migrations_directory(package):
    package_module = import_module(package)
    path_to_module = os.path.dirname(package_module.__file__)
    path_to_migrations = os.path.join(path_to_module, 'migrations')
    if not os.path.exists(path_to_migrations):
        os.mkdir(path_to_migrations)
        init_file_path = os.path.join(path_to_migrations, '__init__.py')
        with open(init_file_path, 'w') as file_descriptor:
            file_descriptor.write(INIT_FILE_TEMPLATE)
    return path_to_migrations


def generate_migration_name(name=None, current_number=0):
    prefix = MIGRATION_NAME_TEMPLATE % (current_number + 1)
    return prefix if not name else '%s_%s.py' % (prefix, name, )


def create_migration_file(path_to_migrations, name):
    migration_file_path = os.path.join(path_to_migrations, name)
    with open(migration_file_path, 'w') as file_descriptor:
        file_descriptor.write(MIGRATION_TEMPLATE)


def get_migrations_list(package, directory=None):
    if not directory:
        directory = get_package_migrations_directory(package)
    result = {}
    for file_name in os.listdir(directory):
        if file_name[DIGITS_IN_MIGRATION_NUMBER] == '_' and file_name.endswith('.py'):
            result[int(file_name[:DIGITS_IN_MIGRATION_NUMBER])] = file_name
    return result


def get_migration_python_path_and_name(name, package):
    migration_module_name = name.strip('.py')
    return '.'.join((package,'migrations', migration_module_name, )), migration_module_name


class DatabaseHelper(object):

    database_api = None
    migration_history_table_name = None

    def __init__(self, database_api, migration_history_table_name):
        self.database_api = database_api
        self.migration_history_table_name = migration_history_table_name

    def migration_history_exists(self):

        sql = '''
        SELECT *
        FROM information_schema.tables
        WHERE table_name=%(history_table_name)s
        '''
        try:
            result = self.database_api.execute(
                sql,
                params={'history_table_name': self.migration_history_table_name},
                return_result='rowcount',
                commit=False
            )
        except ProgrammingError:
            result = None

        return True if result else False

    def get_latest_migration_number(self, package):
        result = 0
        if not self.migration_history_exists():
            self.create_history_table()
        else:
            sql = '''
                SELECT name
                FROM %s
                WHERE package = %%s
                ORDER BY id DESC LIMIT 1;
            ''' % self.migration_history_table_name
            query_params = (package, )

            rows = self.database_api.execute(sql, params=query_params, return_result='fetchall', commit=False)
            if rows:
                name = rows[0][0]
                result = int(name.split('_')[0].strip('0'))

        return result

    def create_history_table(self):

        sql = '''
            CREATE TABLE %s (
                id SERIAL PRIMARY KEY,
                package VARCHAR(200) NOT NULL,
                name VARCHAR(200) NOT NULL,
                processed_at  TIMESTAMP default current_timestamp
            );
        ''' % self.migration_history_table_name
        self.database_api.execute(
            sql, params=(self.migration_history_table_name, ), return_result=None, commit=True
        )

    def write_migration_history(self, name, package):

        sql = '''
            INSERT INTO %s(name, package)
            VALUES (%%s, %%s);
        ''' % self.migration_history_table_name
        self.database_api.execute(sql, params=(name, package, ), return_result=None, commit=True)

    def delete_migration_history(self, name, package):
        sql = '''
            DELETE FROM %s
            WHERE name=%%s and package=%%s
        ''' % self.migration_history_table_name
        self.database_api.execute(sql, params=(name, package, ), return_result=None, commit=True)
