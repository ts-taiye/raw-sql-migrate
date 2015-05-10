# -*- coding: utf-8 -*-

import os

from importlib import import_module


__all__ = (
    'prepare_package_migration_directory',
    'get_package_migrations_directory',
    'get_migration_python_path_and_name',
    'MIGRATION_NAME_TEMPLATE',
    'MIGRATION_TEMPLATE',
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