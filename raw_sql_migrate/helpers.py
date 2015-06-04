# -*- coding: utf-8 -*-

import os

from importlib import import_module

from raw_sql_migrate.exceptions import IncorrectPackage, IncorrectMigrationFile

__all__ = (
    'get_package_migrations_directory',
    'get_file_system_latest_migration_number',
    'get_migration_python_path_and_name',
    'get_empty_migration_file_content',
    'create_migration_file',
    'get_migration_file_content',
    'create_squashed_migration_file',
    'MIGRATION_NAME_TEMPLATE',
    'MIGRATION_TEMPLATE',
    'DatabaseHelper',
)

MIGRATION_NAME_TEMPLATE = '%04d'
PASS_LINE = '    pass'

MIGRATION_TEMPLATE = """# -*- coding: utf-8 -*-

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
INIT_FILE_TEMPLATE = """# -*- coding: utf-8 -*-

"""
DIGITS_IN_MIGRATION_NUMBER = 4


class MigrationDirection(object):
    FORWARD = 'forward'
    BACKWARD = 'backward'


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
            file_descriptor.write(INIT_FILE_TEMPLATE)
    return path_to_migrations


def generate_migration_name(name=None, current_number=1):
    prefix = MIGRATION_NAME_TEMPLATE % current_number
    return prefix if not name else '%s_%s.py' % (prefix, name,)


def get_empty_migration_file_content():
    return MIGRATION_TEMPLATE % (PASS_LINE, PASS_LINE,)


def create_migration_file(path_to_migrations, name):
    migration_file_path = os.path.join(path_to_migrations, name)
    with open(migration_file_path, 'w') as file_descriptor:
        file_descriptor.write(get_empty_migration_file_content())


def create_squashed_migration_file(path_to_migrations, name, forward_content, backward_content):
    migration_file_path = os.path.join(path_to_migrations, name)
    with open(migration_file_path, 'w') as file_descriptor:
        file_descriptor.write(MIGRATION_TEMPLATE % (forward_content, backward_content,))


def get_migrations_list(package, directory=None):
    if not directory:
        directory = get_package_migrations_directory(package)
    result = {}
    for file_name in os.listdir(directory):
        if file_name[DIGITS_IN_MIGRATION_NUMBER] == '_' and file_name.endswith('.py'):
            result[int(file_name[:DIGITS_IN_MIGRATION_NUMBER])] = {
                'file_name': file_name,
                'file_path': os.path.join(directory, file_name),
                'file_directory': directory,
            }
    return result


def get_file_system_latest_migration_number(package):
    data = get_migrations_list(package)
    if not data:
        return 0
    number = sorted(data.keys())[-1]
    return number


def get_migration_python_path_and_name(name, package):
    migration_module_name = name.strip('.py')
    return '.'.join((package, 'migrations', migration_module_name,)), migration_module_name


def get_migration_file_content(file_path):
    with open(file_path, 'r') as descriptor:
        lines = [line for line in descriptor]

    forward_start_index = None
    forward_end_index = None
    backward_start_index = None
    backward_end_index = lines.index(lines[-1])

    for line in lines:
        if 'def forward(' in line:
            forward_start_index = lines.index(line) + 1
        elif 'def backward(' in line:
            forward_end_index = lines.index(line) - 1
            backward_start_index = lines.index(line) + 1
    if forward_start_index is None or forward_end_index is None or backward_start_index is None:
        raise IncorrectMigrationFile('Incorrect migration file found: %s' % file_path)

    return (
        str(lines[forward_start_index:forward_end_index]),
        str(lines[backward_start_index:backward_end_index]),
    )


def get_migration_direction(package_param, current_migration_number, migration_number):
    if package_param is not None and migration_number is not None and migration_number < current_migration_number:
        migration_direction = MigrationDirection.BACKWARD

    elif package_param is not None and migration_number == current_migration_number:
        migration_direction = None
    else:
        migration_direction = MigrationDirection.FORWARD
    return migration_direction


def get_migrations_numbers_to_apply(existing_migrations_numbers, current_migration_number, migration_number, direction):
    if direction == MigrationDirection.FORWARD:
        if migration_number:
            lambda_for_filter = lambda number: current_migration_number < number <= migration_number
        else:
            lambda_for_filter = lambda number: number > current_migration_number
        result = sorted(filter(lambda_for_filter, existing_migrations_numbers))
    else:
        if migration_number:
            lambda_for_filter = lambda number: current_migration_number > number >= migration_number
        else:
            lambda_for_filter = lambda number: number <= current_migration_number
        result = sorted(filter(lambda_for_filter, existing_migrations_numbers), reverse=True)
    return result


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

        result = self.database_api.execute(
            sql,
            params={'history_table_name': self.migration_history_table_name},
            return_result='rowcount',
        )

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
            query_params = (package,)

            rows = self.database_api.execute(sql, params=query_params, return_result='fetchall')
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
            sql, params=(), return_result=None
        )
        self.database_api.commit()

    def drop_history_table(self):

        sql = '''
            DROP TABLE %s;
        ''' % self.migration_history_table_name
        self.database_api.execute(
            sql, params=(self.migration_history_table_name,), return_result=None
        )
        self.database_api.commit()

    def write_migration_history(self, name, package):

        sql = '''
            INSERT INTO %s(name, package)
            VALUES (%%s, %%s);
        ''' % self.migration_history_table_name
        self.database_api.execute(sql, params=(name, package,), return_result=None)
        self.database_api.commit()

    def delete_migration_history(self, name, package):
        sql = '''
            DELETE FROM %s
            WHERE name=%%s and package=%%s
        ''' % self.migration_history_table_name
        self.database_api.execute(sql, params=(name, package,), return_result=None)
        self.database_api.commit()

    def status(self, package=None):
        if package:
            sql = '''
                SELECT DISTINCT(package), name, processed_at
                FROM %s
                WHERE package=%%s
                ORDER BY processed_at DESC;
            ''' % self.migration_history_table_name
            params = (package,)
        else:
            sql = '''
                SELECT DISTINCT(package), name, processed_at
                FROM %s
                ORDER BY processed_at DESC;
            ''' % self.migration_history_table_name
            params = ()

        rows = self.database_api.execute(
            sql, params=params, return_result=self.database_api.CursorResult.FETCHALL
        )
        result = {}
        for row in rows:
            result[row[0]] = {'name': row[1], 'processed_at': row[2]}
        return result
