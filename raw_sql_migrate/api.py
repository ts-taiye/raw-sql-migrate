# -*- coding: utf-8 -*-

from importlib import import_module

from db import (
    migration_history_exists, create_history_table,
    get_latest_migration_number, write_migration_history,
)
from helpers import (
    generate_migration_name, get_package_migrations_directory,
    create_migration_file, get_migrations_list, get_migration_python_path_and_name ,
)


def create(package, name='', config=None):
    """
    :param package: path to package where migration should be created
    :param name: human readable name of migration
    :param config: config instance
    :return: migration name
    """
    if not migration_history_exists(config):
        create_history_table(config)
        current_migration_number = 0
    else:
        current_migration_number = get_latest_migration_number(package, config)
    path_to_migrations = get_package_migrations_directory(package)
    migration_name = generate_migration_name(name, current_migration_number)
    create_migration_file(path_to_migrations, migration_name)


def forward(package, full_forward=False, config=None):
    """
    :param package: path to package which migrations should be applied
    :param full_forward: upgrade to latest migration. Default only one migration forward
    :param config: config instance
    :return: None
    """
    if not migration_history_exists(config):
        create_history_table(config)
        current_migration_number = 0
    else:
        result = get_latest_migration_number(package, config)
        if result:
            current_migration_number = result
        else:
            current_migration_number = 0
    migration_data = get_migrations_list(package)
    new_migrations_numbers = filter(lambda number: number > current_migration_number, migration_data.keys())

    if not new_migrations_numbers:
        print u'Nothing to migrate!'
        return

    for new_migration_number in new_migrations_numbers:
        migration_python_path, name = get_migration_python_path_and_name(migration_data[new_migration_number], package)
        module = import_module(migration_python_path)
        if not hasattr(module, 'forward'):
            raise Exception('%s has no forward function defined')

        module.forward()
        write_migration_history(name, package)



def backward(package, full_backward=False, config=None):
    """
    :param package: path to package which migrations should be reverted
    :param full_backward: downgrade to latest migration. Default only one migration backward
    :param config: config instance
    :return: None
    """
    pass
