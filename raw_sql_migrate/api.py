# -*- coding: utf-8 -*-

from importlib import import_module

from db import DatabaseApi
from exceptions import (
    InconsistentParamsException, NoForwardMigrationsFound, NoBackwardMigrationsFound,
    IncorrectMigrationFile,
)
from helpers import (
    generate_migration_name, get_package_migrations_directory,
    create_migration_file, get_migrations_list, get_migration_python_path_and_name,
    DatabaseHelper,
)

__all__ = (
    'Api',
)


class Api(object):

    config = None
    database_api = None
    database_helper = None

    def __init__(self, config=None):
        self.config = config
        self.database_api = DatabaseApi(config.host, config.port, config.name, config.user, config.password)
        self.database_helper = DatabaseHelper(self.database_api, self.config.history_table_name)

    def create(self, package, name=''):
        """
        :param package: path to package where migration should be created
        :param name: human readable name of migration
        :return: migration name
        """
        if not self.database_helper.migration_history_exists():
            self.database_helper.create_history_table()
            current_migration_number = 0
        else:
            current_migration_number = self.database_helper.get_latest_migration_number(package)
        path_to_migrations = get_package_migrations_directory(package)
        migration_name = generate_migration_name(name, current_migration_number)
        create_migration_file(path_to_migrations, migration_name)

    def forward(self, package, migration_number=None):
        """
        :param package: path to package which migrations should be applied
        :param migration_number: number of migration to migrate to. Can't be used with full_forward. Example: 0042
        :return: None
        """
        current_migration_number = self.database_helper.get_latest_migration_number(package)

        if migration_number and migration_number < current_migration_number:
            raise InconsistentParamsException(
                u'Inconsistent params given: migration number cant\'t be less then current.'
            )

        if not migration_number:
            lambda_for_filter = lambda number: number > current_migration_number
        elif migration_number:
            lambda_for_filter = lambda number: current_migration_number < number <= migration_number
        else:
            lambda_for_filter = lambda number: number == current_migration_number + 1

        migration_data = get_migrations_list(package)
        new_migrations_numbers = filter(lambda_for_filter, migration_data.keys())

        if not new_migrations_numbers:
            raise NoForwardMigrationsFound(u'No new migrations found in package %s' % package)

        for new_migration_number in new_migrations_numbers:
            migration_python_path, name = get_migration_python_path_and_name(
                migration_data[new_migration_number], package
            )
            module = import_module(migration_python_path)
            if not hasattr(module, 'forward'):
                raise IncorrectMigrationFile(u'File %s has no forward function' % migration_python_path)

            module.forward(self.database_api)
            self.database_helper.write_migration_history(name, package)

    def backward(self, package, migration_number=None):
        """
        :param package: path to package which migrations should be reverted
        :param migration_number: migration number to downgrade to. Can't be used with full_backward. Example: 0042
        :return: None
        """
        current_migration_number = self.database_helper.get_latest_migration_number(package)

        if migration_number and migration_number > current_migration_number:
            raise InconsistentParamsException(
                u'Inconsistent params given: migration number cant\'t be less then current.'
            )

        if not migration_number:
            lambda_for_filter = lambda number: number <= current_migration_number
        elif migration_number:
            lambda_for_filter = lambda number: current_migration_number > number >= migration_number
        else:
            lambda_for_filter = lambda number: number == current_migration_number - 1

        migration_data = get_migrations_list(package)
        previous_migrations_numbers = filter(lambda_for_filter, migration_data.keys())

        if not previous_migrations_numbers:
            raise NoBackwardMigrationsFound(
                u'No backward migrations found in to downgrade from %s' % current_migration_number
            )

        for previous_migration_number in previous_migrations_numbers:
            migration_python_path, name = get_migration_python_path_and_name(
                migration_data[previous_migration_number], package
            )
            module = import_module(migration_python_path)
            if not hasattr(module, 'backward'):
                raise IncorrectMigrationFile(u'File %s has no backward function' % migration_python_path)

            module.backward(self.database_api)
            self.database_helper.delete_migration_history(name, package)
