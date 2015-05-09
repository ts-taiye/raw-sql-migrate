# -*- coding: utf-8 -*-

import os

from importlib import import_module


__all__ = (
    'prepare_package_migration_directory',
    'generate_migration_name',
    'MIGRATION_NAME_TEMPLATE',
    'MIGRATION_TEMPLATE',
)

MIGRATION_NAME_TEMPLATE = '%04d'
MIGRATION_TEMPLATE = """# encoding: utf-8

from raw_sql_migrate.db import execute


def forward():
    pass


def backward():
    pass

"""


def prepare_package_migration_directory(package):
    package_module = import_module(package)
    path_to_module = os.path.dirname(package_module.__file__)
    path_to_migrations = os.path.join(path_to_module, 'migrations')
    if not os.path.exists(path_to_migrations):
        os.mkdir(path_to_migrations)
    return path_to_migrations


def generate_migration_name(name=None, current_number=0):
    prefix = MIGRATION_NAME_TEMPLATE % (current_number + 1)
    return prefix if not name else '%s_%s.py' % (prefix, name, )


def create_migration_file(path_to_migrations, name):
    destination_file = os.path.join(path_to_migrations, name)
    file_descriptor = open(destination_file, 'w')
    file_descriptor.write(MIGRATION_TEMPLATE)
    file_descriptor.close()
