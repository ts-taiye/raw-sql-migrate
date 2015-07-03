# -*- coding: utf-8 -*-

import os

from importlib import import_module

from raw_sql_migrate import rsm_config
from raw_sql_migrate.engines import database_api
from raw_sql_migrate.exceptions import IncorrectPackage, IncorrectMigrationFile

__all__ = (
    'FileSystemHelper',
    'MigrationHelper',
    'DatabaseHelper',
)


class FileSystemHelper(object):

    @staticmethod
    def get_package_migrations_directory(package):
        try:
            package_module = import_module(package)
        except ImportError:
            raise IncorrectPackage(u'Failed to import package %s.' % package)

        path_to_module = os.path.dirname(package_module.__file__)
        path_to_migrations = os.path.join(path_to_module, 'migrations')
        if not os.path.exists(path_to_migrations):
            os.mkdir(path_to_migrations)
            init_file_path = os.path.join(path_to_migrations, '__init__.py')
            with open(init_file_path, 'w+') as file_descriptor:
                file_descriptor.write(MigrationHelper.INIT_FILE_TEMPLATE)
        return path_to_migrations

    @classmethod
    def get_file_system_latest_migration_number(cls, package):
        data = cls.get_migrations_list(package)
        if not data:
            return 0
        number = sorted(data.keys())[-1]
        return number

    @classmethod
    def get_migrations_list(cls, package, directory=None):
        if not directory:
            directory = FileSystemHelper.get_package_migrations_directory(package)
        result = {}
        for file_name in os.listdir(directory):
            if file_name[MigrationHelper.DIGITS_IN_MIGRATION_NUMBER] == '_' and file_name.endswith('.py'):
                result[int(file_name[:MigrationHelper.DIGITS_IN_MIGRATION_NUMBER])] = {
                    'file_name': file_name,
                    'file_path': os.path.join(directory, file_name),
                    'file_directory': directory,
                }
        return result

    @staticmethod
    def get_migration_python_path_and_name(name, package):
        migration_module_name = name.strip('.py')
        return '.'.join((package, 'migrations', migration_module_name,)), migration_module_name

    @staticmethod
    def get_migration_file_content(file_path):
        with open(file_path, 'r') as descriptor:
            lines = [line for line in descriptor]

        forward_start_index = None
        forward_end_index = None
        backward_start_index = None
        backward_end_index = len(lines)

        for line in lines:
            if 'def forward(' in line:
                forward_start_index = lines.index(line) + 1
            elif 'def backward(' in line:
                forward_end_index = lines.index(line) - 1
                backward_start_index = lines.index(line) + 1
        if forward_start_index is None or forward_end_index is None or backward_start_index is None:
            raise IncorrectMigrationFile('Incorrect migration file found: %s' % file_path)

        return (
            ''.join(lines[forward_start_index:forward_end_index]).replace('\n\n', '\n'),
            ''.join(lines[backward_start_index:backward_end_index]).replace('\n\n', '\n'),
        )


class MigrationHelper(object):

    MIGRATION_NAME_TEMPLATE = '%04d'
    PASS_LINE = '    pass'
    MIGRATION_TEMPLATE = """
# -*- coding: utf-8 -*-

# Use database_api execute method to call raw sql query.
# execute(sql, params=None, return_result=None)
#   sql: Raw SQL query
#   params: arguments dict for query
#   return_result: type of query result, constants for it
#       are located in database_api.CursorResults class. Possible variants: ROWCOUNT, FETCHALL


def forward(database_api):
%s


def backward(database_api):
%s
"""
    INIT_FILE_TEMPLATE = """
# -*- coding: utf-8 -*-

"""
    DIGITS_IN_MIGRATION_NUMBER = 4

    class MigrationDirection(object):
        FORWARD = 'forward'
        BACKWARD = 'backward'

    @classmethod
    def generate_migration_name(cls, name=None, current_number=1):
        prefix = cls.MIGRATION_NAME_TEMPLATE % current_number
        return prefix if not name else '%s_%s.py' % (prefix, name,)

    @classmethod
    def get_empty_migration_file_content(cls):
        return cls.MIGRATION_TEMPLATE % (cls.PASS_LINE, cls.PASS_LINE,)

    @classmethod
    def create_migration_file(cls, path_to_migrations, name):
        migration_file_path = os.path.join(path_to_migrations, name)
        with open(migration_file_path, 'w') as file_descriptor:
            file_descriptor.write(cls.get_empty_migration_file_content())

    @classmethod
    def create_squashed_migration_file(cls, path_to_migrations, name, forward_content, backward_content):
        migration_file_path = os.path.join(path_to_migrations, name)
        with open(migration_file_path, 'w') as file_descriptor:
            file_descriptor.write(cls.MIGRATION_TEMPLATE % (forward_content, backward_content,))

    @classmethod
    def get_migration_direction(cls, package_param, current_migration_number, migration_number):
        if package_param is not None and migration_number is not None and migration_number < current_migration_number:
            migration_direction = cls.MigrationDirection.BACKWARD

        elif package_param is not None and migration_number == current_migration_number:
            migration_direction = None
        else:
            migration_direction = cls.MigrationDirection.FORWARD
        return migration_direction

    @classmethod
    def get_migrations_numbers_to_apply(
            cls, existing_migrations_numbers, current_migration_number, migration_number, direction
    ):
        if direction == cls.MigrationDirection.FORWARD:
            reverse = False
            if migration_number:
                lambda_for_filter = lambda number: current_migration_number < number <= migration_number
            else:
                lambda_for_filter = lambda number: number > current_migration_number
        else:
            reverse = True
            if migration_number:
                lambda_for_filter = lambda number: current_migration_number >= number > migration_number
            else:
                lambda_for_filter = lambda number: number <= current_migration_number
        result = sorted(filter(lambda_for_filter, existing_migrations_numbers), reverse=reverse)
        return result


class DatabaseHelper(object):

    @staticmethod
    def migration_history_exists():

        sql = '''
            SELECT *
            FROM information_schema.tables
            WHERE table_name=%(history_table_name)s
        '''

        result = database_api.execute(
            sql,
            params={'history_table_name': rsm_config.history_table_name},
            return_result='rowcount',
        )

        return True if result else False

    @classmethod
    def get_latest_migration_number(cls, package):
        result = 0
        if not cls.migration_history_exists():
            cls.create_history_table()
        else:
            sql = '''
                SELECT name
                FROM %s
                WHERE package = %%s
                ORDER BY id DESC LIMIT 1;
            ''' % rsm_config.history_table_name
            query_params = (package,)

            rows = database_api.execute(sql, params=query_params, return_result='fetchall')
            if rows:
                name = rows[0][0]
                result = int(name.split('_')[0].strip('0'))

        return result

    @staticmethod
    def create_history_table():

        sql = '''
            CREATE TABLE %s (
                id SERIAL PRIMARY KEY,
                package VARCHAR(200) NOT NULL,
                name VARCHAR(200) NOT NULL,
                processed_at  TIMESTAMP default current_timestamp
            );
        ''' % rsm_config.history_table_name
        database_api.execute(
            sql, params=(), return_result=None
        )
        database_api.commit()

    @staticmethod
    def drop_history_table():

        sql = '''
            DROP TABLE %s;
        ''' % rsm_config.history_table_name
        database_api.execute(
            sql, params=(rsm_config.history_table_name,), return_result=None
        )
        database_api.commit()

    @staticmethod
    def write_migration_history(name, package):

        sql = '''
            INSERT INTO %s(name, package)
            VALUES (%%s, %%s);
        ''' % rsm_config.history_table_name
        database_api.execute(sql, params=(name, package, ), return_result=None)

    @staticmethod
    def delete_migration_history(name, package):
        sql = '''
            DELETE FROM %s
            WHERE name=%%s and package=%%s
        ''' % rsm_config.history_table_name
        database_api.execute(sql, params=(name, package, ), return_result=None)

    @staticmethod
    def status(package=None):
        migration_history_param = (rsm_config.history_table_name, ) * 2
        if package:
            sql = '''
                SELECT package, name, processed_at FROM  %s
                WHERE id IN (
                    SELECT max(id)
                    FROM %s
                    GROUP BY package
                )
                AND package = %%s
                ORDER BY package;
            '''
            params = (package, )
        else:
            sql = '''
                SELECT package, name, processed_at FROM  %s
                WHERE id IN (
                    SELECT max(id)
                    FROM %s
                    GROUP BY package
                ) ORDER BY package;
            '''
            params = ()
        sql = sql % migration_history_param
        rows = database_api.execute(
            sql, params=params, return_result=database_api.CursorResult.FETCHALL
        )
        result = {}
        for row in rows:
            result[row[0]] = {'name': row[1], 'processed_at': row[2]}
        return result
