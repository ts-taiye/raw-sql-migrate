# -*- coding: utf-8 -*-

from os import rename, path
from sys import stdout

from importlib import import_module

from raw_sql_migrate import config as file_config
from raw_sql_migrate.exceptions import (
    InconsistentParamsException, NoMigrationsFoundToApply,
    IncorrectMigrationFile, ParamRequiredException, IncorrectDbBackendException,
)
from raw_sql_migrate.helpers import (
    generate_migration_name, get_package_migrations_directory,
    create_migration_file, get_migrations_list, get_migration_python_path_and_name,
    get_migration_file_content, create_squashed_migration_file, get_file_system_latest_migration_number,
    get_migration_direction, get_migrations_numbers_to_apply,
    DatabaseHelper, MigrationDirection,
)

__all__ = (
    'Api',
)


class Api(object):

    config = None
    database_api = None
    database_helper = None

    def __init__(self, config=None):

        if config is not None:
            self.config = config
        else:
            self.config = file_config

        try:
            database_api_module = import_module(self.config.engine)
            self.database_api = database_api_module.DatabaseApi(
                self.config.host,
                self.config.port,
                self.config.name,
                self.config.user,
                self.config.password,
                self.config.additional_connection_params
            )
        except (ImportError, AttributeError, ):
            raise IncorrectDbBackendException(u'Failed to import given database engine: %s' % self.config.engine)

        self.database_helper = DatabaseHelper(self.database_api, self.config.history_table_name)

    def _create_migration_history_table_if_not_exists(self):
        if not self.database_helper.migration_history_exists():
            self.database_helper.create_history_table()

    def _prepare_migration_data(self, package, migration_number):
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
            if self.config.packages:
                packages = self.config.packages
            else:
                raise InconsistentParamsException(
                    'Inconsistent params: specify package or packages list in config'
                )
        else:
            raise InconsistentParamsException(
                'Inconsistent params: can\'t apply one migration number to all packages, please give one or remove\n'
                'migration number.\n'
            )
        return package, packages, migration_number

    def _migrate(self, package, file_name, migration_direction):
        migration_python_path, name = get_migration_python_path_and_name(
            file_name, package
        )
        module = import_module(migration_python_path)
        handler = getattr(module, migration_direction, None)
        if not handler:
            raise IncorrectMigrationFile('File %s has no %s function' % (
                migration_python_path, migration_direction,
            ))

        stdout.write('Migrating %s to migration %s in package %s\n' % (
            migration_direction, name, package,
        ))
        try:
            handler(self.database_api)
            self.database_api.commit()
            if migration_direction == MigrationDirection.FORWARD:
                self.database_helper.write_migration_history(name, package)
            else:
                self.database_helper.delete_migration_history(name, package)
        except Exception as e:
            self.database_api.rollback()
            raise e

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

        current_migration_number = get_file_system_latest_migration_number(package)
        path_to_migrations = get_package_migrations_directory(package)
        migration_name = generate_migration_name(name, current_migration_number + 1)
        create_migration_file(path_to_migrations, migration_name)

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

        package, packages, migration_number = self._prepare_migration_data(package, migration_number)

        self._create_migration_history_table_if_not_exists()

        migration_direction = None
        for package_for_migrate in packages:
            current_migration_number = self.database_helper.get_latest_migration_number(package_for_migrate)
            if not migration_direction:
                migration_direction = get_migration_direction(package, current_migration_number, migration_number)
                if migration_direction is None:
                    raise InconsistentParamsException('Current migration number matches given one')

            migration_data = get_migrations_list(package_for_migrate)
            numbers_to_apply = get_migrations_numbers_to_apply(
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
                self._migrate(
                    package_for_migrate,
                    migration_data[migration_number_to_apply]['file_name'],
                    migration_direction
                )

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

        return self.database_helper.status(package)

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

        current_migration_number = self.database_helper.get_latest_migration_number(package)
        last_file_system_migration_number = get_file_system_latest_migration_number(package)

        if begin_from:
            begin_from = int(begin_from)

        if begin_from <= current_migration_number or current_migration_number > last_file_system_migration_number:
            raise InconsistentParamsException(
                'Can squash only applied migrations. Current applied migration number is %s' % current_migration_number
            )

        if begin_from < 1:
            raise InconsistentParamsException(
                'begin_from should be not less than 1'
            )

        migration_data = get_migrations_list(package)
        ordered_keys = sorted(migration_data.keys())

        for key in ordered_keys[begin_from:]:
            file_name = migration_data[key]['file_name']
            file_path = migration_data[key]['file_path']
            stdout.write('Squashing migration %s...' % file_name)
            file_forward_content, file_backward_content = get_migration_file_content(file_path)
            result_forward_content += file_forward_content
            result_backward_content += file_backward_content
            new_file_name = 'squashed_%s' % file_name
            new_file_path = path.join(migration_data[key]['file_directory'], new_file_name)
            rename(migration_data[key]['file_path'], new_file_path)
        last_number = ordered_keys[-1]
        if name is None:
            name = '%04d_squashed_%04d_to_%04d.py' % (begin_from, begin_from, last_number, )
        else:
            name = generate_migration_name(name, begin_from)
        path_to_package_migrations = get_package_migrations_directory(package)
        create_squashed_migration_file(
            path_to_package_migrations, name, result_forward_content, result_backward_content
        )
