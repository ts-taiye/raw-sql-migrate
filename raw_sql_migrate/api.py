# -*- coding: utf-8 -*-

from db import check_if_migration_history_exists, create_history_table
from helpers import generate_migration_name, prepare_package_migration_directory, create_migration_file


def create(package, name='', config=None):
    """
    :param package: path to package where migration should be created
    :param name: human readable name of migration
    :param config: config instance
    :return: migration name
    """
    if not check_if_migration_history_exists(config):
        create_history_table(config)
        current_migration_number = 0
    else:
        current_migration_number = 1
    path_to_migrations = prepare_package_migration_directory(package)
    migration_name = generate_migration_name(name, current_migration_number)
    create_migration_file(path_to_migrations, migration_name)


def forward(package, full_forward=False, config=None):
    """
    :param package: path to package which migrations should be applied
    :param full_forward: upgrade to latest migration. Default only one migration forward
    :param config: config instance
    :return: None
    """
    pass


def backward(package, full_backward=False, config=None):
    """
    :param package: path to package which migrations should be reverted
    :param full_backward: downgrade to latest migration. Default only one migration backward
    :param config: config instance
    :return: None
    """
    pass
