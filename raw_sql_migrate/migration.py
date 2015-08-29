# -*- coding: utf-8 -*-

from os import path

from importlib import import_module
from sys import stdout

from raw_sql_migrate import rsm_config
from raw_sql_migrate.helpers import MigrationHelper, FileSystemHelper, DatabaseHelper
from raw_sql_migrate.engines import database_api
from raw_sql_migrate.exceptions import IncorrectMigrationFile

__all__ = (
    'Migration',
)


class Migration(object):
    """
    Migration module wrapper
    :var py_package: string containing python path to package.
    Example: package_a.package_b
    :var py_migration_package: string containing python migration package of given package
    Example: package_a.package_b.migrations
    :var py_module_name: string containing python module name
    Example: 0001_initial
    :var fs_migration_directory: string containing file system path to migration_directory
    Example: ../package_a/package_b/migrations/
    :var fs_file_name: string containing file name of migration
    Example: 0001_initial.py
    :var module: module object of migration
    """
    py_package = None
    py_migration_package = None
    py_module_name = None
    py_module = None
    fs_migration_directory = None
    fs_file_name = None
    module = None

    def __init__(self, py_package, py_module_name=None):
        self.py_package = py_package
        self.fs_migration_directory = FileSystemHelper.get_package_migrations_directory(py_package)
        self.py_module_name = py_module_name.rstrip('.py')
        self.fs_file_name = '%s.py' % py_module_name
        self.py_module, self.py_module_name = FileSystemHelper.get_migration_python_path_and_name(
            py_module_name, py_package
        )
        self.module = import_module(self.py_module)

    def migrate(self, migration_direction):
        """
        Migrates migration found in self.module towards to given direction.
        :param migration_direction: Direction towards which to migrate. Can be forward or backward.
        :return:
        """

        assert self.module is not None

        if hasattr(self.module, migration_direction):
            handler = getattr(self.module, migration_direction)
            stdout.write('Migrating %s to migration %s in package %s\n' % (
                migration_direction, self.py_module_name, self.py_package,
            ))
        else:
            raise IncorrectMigrationFile('Module %s has no %s function' % (
                self.module, migration_direction,
            ))

        try:
            handler(database_api)
            if migration_direction == MigrationHelper.MigrationDirection.FORWARD:
                self.write_migration_history()
            else:
                self.delete_migration_history()
            database_api.commit()
        except Exception as e:
            if not database_api._connection.closed:
                database_api.rollback()
                database_api._connection.close()
            raise e

    def write_migration_history(self):
        """
        Writes migrate history entity for given migration
        :return:
        """
        DatabaseHelper.write_migration_history(self.py_module_name, self.py_package)

    def delete_migration_history(self):
        """
        Deletes migrate history entity in DB for given migration
        :return:
        """
        DatabaseHelper.delete_migration_history(self.py_module_name, self.py_package)

    @staticmethod
    def create(py_package, name):
        """
        Creates new migration and binds current instance to result module
        :param name: new migration name given by user. Example: initial
        :return:
        """
        current_migration_number = FileSystemHelper.get_file_system_latest_migration_number(py_package)
        fs_migration_directory = FileSystemHelper.get_package_migrations_directory(py_package)
        fs_file_name = MigrationHelper.generate_migration_name(name, current_migration_number + 1)
        MigrationHelper.create_migration_file(fs_migration_directory, fs_file_name)
        return Migration(py_package, fs_file_name.rstrip('.py'))

    @staticmethod
    def create_squashed(py_package, name, migration_number, forward_content, backward_content):
        """
        Creates squashed migration and binds current instance to result module
        :param name: new migration name given by user. Example: initial
        :param migration_number: first squashed migration number
        :param forward_content: forward content of all squashed migrations
        :param backward_content: backward content of all squashed migrations
        :return:
        """
        if name is None:
            name = '%04d_squashed.py' % migration_number
        else:
            name = MigrationHelper.generate_migration_name(name, migration_number)
        fs_migration_directory = FileSystemHelper.get_package_migrations_directory(py_package)
        fs_file_path = path.join(fs_migration_directory, name)
        with open(fs_file_path, 'w') as file_descriptor:
            file_descriptor.write(MigrationHelper.MIGRATION_TEMPLATE % (forward_content, backward_content, ))
        return Migration(py_package, name.rstrip('.py'))
