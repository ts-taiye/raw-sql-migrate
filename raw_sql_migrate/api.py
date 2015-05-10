# -*- coding: utf-8 -*-

from importlib import import_module

from db import (
    migration_history_exists, create_history_table,
    get_latest_migration_number, write_migration_history,
)
from exceptions import InconsistentParamsException, NoNewMigrationsFoundException, IncorrectMigrationFile
from helpers import (
    generate_migration_name, get_package_migrations_directory,
    create_migration_file, get_migrations_list, get_migration_python_path_and_name,
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


def forward(package, full_forward=False, migration_number=None, config=None):
    """
    :param package: path to package which migrations should be applied
    :param full_forward: upgrade to latest migration. Default only one migration forward
    :param migration_number: number of migration to migrate to. Can't be used with full_forward
    :param config: config instance
    :return: None
    """
    if full_forward and migration_number:
        raise InconsistentParamsException(
            u'Inconsistent params given: full_forward and migration number cant\'t be used together.'
        )

    if not migration_history_exists(config):
        create_history_table(config)
        current_migration_number = 0
    else:
        result = get_latest_migration_number(package, config)
        if result:
            current_migration_number = result
        else:
            current_migration_number = 0

    if migration_number and migration_number < current_migration_number:
        raise InconsistentParamsException(
            u'Inconsistent params given: migration number cant\'t be less then current.'
        )

    if full_forward:
        lambda_for_filter = lambda number: number > current_migration_number
    elif migration_number:
        lambda_for_filter = lambda number: current_migration_number < number <= migration_number
    else:
        lambda_for_filter = lambda number: number == current_migration_number + 1

    migration_data = get_migrations_list(package)
    new_migrations_numbers = filter(lambda_for_filter, migration_data.keys())

    if not new_migrations_numbers:
        raise NoNewMigrationsFoundException(u'No new migrations found in package %s' % package)

    for new_migration_number in new_migrations_numbers:
        migration_python_path, name = get_migration_python_path_and_name(migration_data[new_migration_number], package)
        module = import_module(migration_python_path)
        if not hasattr(module, 'forward'):
            raise IncorrectMigrationFile(u'File %s has no forward function' % migration_python_path)

        module.forward()
        write_migration_history(name, package)



def backward(package, full_backward=False, config=None):
    """
    :param package: path to package which migrations should be reverted
    :param full_backward: downgrade to latest migration. Default only one migration backward
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

