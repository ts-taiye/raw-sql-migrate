# -*- coding: utf-8 -*-

from os import rename, path
from sys import stdout

from importlib import import_module

from raw_sql_migrate import Config, rsm_config
from raw_sql_migrate.engines import database_api
from raw_sql_migrate.exceptions import (
    InconsistentParamsException, NoMigrationsFoundToApply,
    ParamRequiredException, IncorrectDbBackendException,
)
from raw_sql_migrate.helpers import FileSystemHelper, MigrationHelper, DatabaseHelper
from raw_sql_migrate.migration import Migration

__all__ = (
    'Api',
)


class Api(object):

    database_helper = None

    def __init__(self, config=None):

        if config is not None:
            config_instance = config
        else:
            config_instance = Config()
            config_instance.init_from_file()
        rsm_config.set_config_instance(config_instance)

        try:
            database_api_module = import_module(config.engine)
            database_api.set_database_api(database_api_module.DatabaseApi(
                config.host,
                config.port,
                config.name,
                config.user,
                config.password,
                config.additional_connection_params
            ))
        except (ImportError, AttributeError, ):
            raise IncorrectDbBackendException(u'Failed to import given database engine: %s' % config.engine)

    @staticmethod
    def _create_migration_history_table_if_not_exists():
        if not DatabaseHelper.migration_history_exists():
            DatabaseHelper.create_history_table()

    @staticmethod
    def _prepare_migration_data(package, migration_number):
        if package:
            package = str(package)

        if migration_number:
            try:
                migration_number = int(migration_number)
            except (TypeError, ValueError, ):
                raise InconsistentParamsException('Incorrect migration number is given')

        if package is not None:
            packages = (package, )
        elif package is None and migration_number is None:
            if rsm_config.packages:
                packages = rsm_config.packages
            else:
                raise InconsistentParamsException(
                    'Inconsistent params: specify package or packages list in config'
                )
        else:
            raise InconsistentParamsException(
                'Inconsistent params: can\'t apply one migration number to all packages, please give one or remove\n'
                'migration number.\n'
            )
        return packages, migration_number

    def create(self, package, name):
        """
        Creates a new migration in given package. Command makes next things:
        1. creates migration structure if package does not have one
        2. creates migration history table if it does not exist
        3. makes new migration file with given name in migration folder
        :param package: path to package where migration should be created
        :param name: human readable name of migration
        :return: migration name
        :raises ParamRequiredException: raises if 'package' or 'name' are not given.
        """
        if not package:
            raise ParamRequiredException('Provide correct package where to store migrations')

        if not name:
            raise ParamRequiredException('Provide correct migration name')

        self._create_migration_history_table_if_not_exists()

        migration = Migration.create(
            py_package=package,
            name=name
        )
        return migration.fs_file_name

    def migrate(self, package=None, migration_number=None):
        """
        Migrates given package or config packages. Usage:
            migrate(package='package_a') - forwards to latest available migration
            migrate(package='package_a', migration_number=42) - if migration number is greater than current
        applied migration migrates forward to 42 migration, else backward.
            migrate() - migrates all packages found in config 'packages' section to latest available migrations
        :param package: package to search migrations in, if not provided tries to get all packages from
        'packages' config section. If found applies migration to all of them.
        :param migration_number: number of migration to apply. If number is behind of current migration
        system migrates back to given number, else migrates forward. If none is provided migrates to
        latest available.
        :return: None
        :raises InconsistentParamsException: raises when:
        1. package or 'packages' section are not provided
        2. package is not provided but migration_number is given
        3. given migration_number in package is given for migrate is equal to current applied
        4. incorrect migration number is given
        :raises NoMigrationsFoundToApply: raises when in the given package there are no migration to apply
        :raises IncorrectMigrationFile: raises when migration file has no forward or backward function
        """

        packages, migration_number = self._prepare_migration_data(package, migration_number)

        self._create_migration_history_table_if_not_exists()

        migration_direction = None
        for package_for_migrate in packages:
            current_migration_number = DatabaseHelper.get_latest_migration_number(package_for_migrate)
            if not migration_direction:
                migration_direction = MigrationHelper.get_migration_direction(
                    package_for_migrate, current_migration_number, migration_number
                )
                if migration_direction is None:
                    raise InconsistentParamsException('Current migration number matches given one')

            migration_data = FileSystemHelper.get_migrations_list(package_for_migrate)
            numbers_to_apply = MigrationHelper.get_migrations_numbers_to_apply(
                migration_data.keys(),
                current_migration_number,
                migration_number,
                migration_direction
            )

            if not numbers_to_apply:
                if package is not None:
                    raise NoMigrationsFoundToApply('No new migrations found in package %s' % package_for_migrate)
                else:
                    stdout.write('No new migrations found in package %s. Skipping.\n' % package_for_migrate)
                    continue

            for migration_number_to_apply in numbers_to_apply:
                file_name = migration_data[migration_number_to_apply]['file_name']
                migration = Migration(
                    py_package=package_for_migrate,
                    py_module_name=file_name
                )
                migration.migrate(migration_direction)

    def status(self, package=None):
        """
        Returns status dictionary for given package or all packages in migration history
        if 'package' is left None. Dictionary has next structure:
        {
            package:
            {
                name: migration name,
                processed_at: datetime of migration apply
            }
        }
        :param package: given status of the given package
        """
        self._create_migration_history_table_if_not_exists()

        return DatabaseHelper.status(package)

    def squash(self, package, begin_from=1, name=None):
        """
        Squashes several migrations into one. Command reads all not applied migrations
        in package migration directory and appends content of forward and backward
        function into result functions. Squash also renames squashed migration with
        'squashed_' prefix.
        :param package: path to package which migrations should be squashed
        :param begin_from: migration number to begin squash from. Should be not less than 1
        :param name: squashed migration name
        """
        result_forward_content = ''
        result_backward_content = ''

        self._create_migration_history_table_if_not_exists()

        current_migration_number = DatabaseHelper.get_latest_migration_number(package)
        last_file_system_migration_number = FileSystemHelper.get_file_system_latest_migration_number(package)

        if begin_from:
            begin_from = int(begin_from)

        if begin_from <= current_migration_number or current_migration_number > last_file_system_migration_number:
            raise InconsistentParamsException(
                'Can squash only migrations which are not applied. Current applied migration number is %s'
                % current_migration_number
            )

        if begin_from < 1:
            raise InconsistentParamsException(
                'begin_from should not be less than 1'
            )

        migration_data = FileSystemHelper.get_migrations_list(package)
        ordered_keys = sorted(migration_data.keys())

        for key in ordered_keys[begin_from:]:
            file_name = migration_data[key]['file_name']
            file_path = migration_data[key]['file_path']
            stdout.write('Squashing migration %s...' % file_name)
            file_forward_content, file_backward_content = FileSystemHelper.get_migration_file_content(file_path)
            result_forward_content += file_forward_content
            result_backward_content += file_backward_content
            new_file_name = 'squashed_%s' % file_name
            new_file_path = path.join(migration_data[key]['file_directory'], new_file_name)
            rename(migration_data[key]['file_path'], new_file_path)

        first_migration_number = ordered_keys[0]

        Migration.create_squashed(
            py_package=package,
            name=name,
            migration_number=first_migration_number,
            forward_content=result_forward_content,
            backward_content=result_backward_content
        )
