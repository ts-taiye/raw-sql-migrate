# -*- coding: utf-8 -*-

from os.path import exists, join

from tests.base import BaseTestCase

from raw_sql_migrate.exceptions import IncorrectPackage
from raw_sql_migrate.helpers import FileSystemHelper, MigrationHelper


__all__ = (
    'GenerateMigrationNameTestCase',
    'MigrationDirectoryCreationTestCase',
    'MigrationFileCreationTestCase',
    'MigrationListTestCase',
    'GetMigrationPythonPathAndNameTestCase',
)


class GenerateMigrationNameTestCase(BaseTestCase):

    def test_positive_case(self):
        name = 'abc'
        self.assertEqual(
            MigrationHelper.generate_migration_name(name),
            '%s_%s.py' % (MigrationHelper.MIGRATION_NAME_TEMPLATE % 1, name)
        )

    def test_incorrect_number_given(self):
        name = 'abc'
        self.assertRaises(TypeError, MigrationHelper.generate_migration_name, name, object())


class MigrationDirectoryCreationTestCase(BaseTestCase):

    def test_directory_created(self):
        path = FileSystemHelper.get_package_migrations_directory(
            self.python_path_to_test_package
        )
        self.assertTrue(exists(self.file_system_test_migrations_path))
        self.assertTrue(exists(self.file_system_path_to_init_py_in_migrations_directory))
        self.assertEqual(path, self.file_system_test_migrations_path)

    def test_unknown_package(self):
        self.assertRaises(IncorrectPackage, FileSystemHelper.get_package_migrations_directory, 'a.b.c')


class MigrationFileCreationTestCase(BaseTestCase):

    migration_file_name = '0001_test.py'

    def setUp(self):
        FileSystemHelper.get_package_migrations_directory(self.python_path_to_test_package)

    def test_empty_migration_file_content(self):
        self.assertEqual(
            MigrationHelper.get_empty_migration_file_content(),
            MigrationHelper.MIGRATION_TEMPLATE % (MigrationHelper.PASS_LINE, MigrationHelper.PASS_LINE, ))

    def test_migration_file_is_created(self):
        MigrationHelper.create_migration_file(self.file_system_test_migrations_path, self.migration_file_name)
        path_to_file = join(self.file_system_test_migrations_path, self.migration_file_name)
        self.assertTrue(exists(path_to_file))
        with open(path_to_file, 'r') as file_descriptor:
            content = file_descriptor.read()
        self.assertEqual(MigrationHelper.get_empty_migration_file_content(), content)


class MigrationListTestCase(BaseTestCase):

    migration_file_names = ('0001_test.py', '0002_test.py', )

    def setUp(self):
        self.migrations_path = FileSystemHelper.get_package_migrations_directory(self.python_path_to_test_package)
        for name in self.migration_file_names:
            MigrationHelper.create_migration_file(self.migrations_path, name)

    def test_all_files_found(self):
        result = FileSystemHelper.get_migrations_list(self.python_path_to_test_package)
        self.assertTrue(len(result), len(self.migration_file_names))

    def test_bad_files_are_ignored(self):
        bad_file_names = ('abc.py', '0001_test.txt', )
        for file_name in bad_file_names:
            MigrationHelper.create_migration_file(self.file_system_test_migrations_path, file_name)
        result = FileSystemHelper.get_migrations_list(self.python_path_to_test_package)
        self.assertEqual(len(result), len(self.migration_file_names))


class GetMigrationPythonPathAndNameTestCase(BaseTestCase):

    migration_name = '0001_test.py'

    def setUp(self):
        path = FileSystemHelper.get_package_migrations_directory(self.python_path_to_test_package)
        MigrationHelper.create_migration_file(path, self.migration_name)

    def test_correct_result(self):
        path, name = FileSystemHelper.get_migration_python_path_and_name(
            self.migration_name, self.python_path_to_test_package
        )
        self.assertEqual(name, self.migration_name.replace('.py', ''))
        self.assertEqual(path, '.'.join((self.python_path_to_test_package, 'migrations', name)))
