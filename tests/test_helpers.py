# -*- coding: utf-8 -*-

from os.path import exists, join

from tests.base import BaseTestCase

from raw_sql_migrate.exceptions import IncorrectPackage
from raw_sql_migrate.helpers import (
    generate_migration_name, MIGRATION_NAME_TEMPLATE, MIGRATION_TEMPLATE,
    get_package_migrations_directory, create_migration_file,
    get_migrations_list, get_migration_python_path_and_name,
)


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
        self.assertEqual(generate_migration_name(name), '%s_%s.py' % (MIGRATION_NAME_TEMPLATE % 1, name))

    def test_incorrect_number_given(self):
        name = 'abc'
        self.assertRaises(TypeError, generate_migration_name, name, object())


class MigrationDirectoryCreationTestCase(BaseTestCase):

    def tearDown(self):
        self._remove_test_migrations_directory()

    def test_directory_created(self):
        path = get_package_migrations_directory(self.python_path_to_test_package)
        self.assertTrue(exists(self.file_system_test_migrations_path))
        self.assertTrue(exists(self.file_system_path_to_init_py_in_migrations_directory))
        self.assertEqual(path, self.file_system_test_migrations_path)

    def test_unknown_package(self):
        self.assertRaises(IncorrectPackage, get_package_migrations_directory, 'a.b.c')


class MigrationFileCreationTestCase(BaseTestCase):

    migration_file_name = '0001_test.py'

    def setUp(self):
        get_package_migrations_directory(self.python_path_to_test_package)

    def tearDown(self):
        self._remove_test_migrations_directory()

    def test_migration_file_is_created(self):
        create_migration_file(self.file_system_test_migrations_path, self.migration_file_name)
        path_to_file = join(self.file_system_test_migrations_path, self.migration_file_name)
        self.assertTrue(exists(path_to_file))
        with open(path_to_file, 'r') as file_descriptor:
            content = file_descriptor.read()
        self.assertEqual(MIGRATION_TEMPLATE, content)


class MigrationListTestCase(BaseTestCase):

    migration_file_names = ('0001_test.py', '0002_test.py', )

    def setUp(self):
        self.migrations_path = get_package_migrations_directory(self.python_path_to_test_package)
        for name in self.migration_file_names:
            create_migration_file(self.migrations_path, name)

    def tearDown(self):
        self._remove_test_migrations_directory()

    def test_all_files_found(self):
        result = get_migrations_list(self.python_path_to_test_package)
        self.assertTrue(len(result), len(self.migration_file_names))

    def test_bad_files_are_ignored(self):
        bad_file_names = ('abc.py', '0001_test.txt', )
        for file_name in bad_file_names:
            create_migration_file(self.file_system_test_migrations_path, file_name)
        result = get_migrations_list(self.python_path_to_test_package)
        self.assertEqual(len(result), len(self.migration_file_names))


class GetMigrationPythonPathAndNameTestCase(BaseTestCase):

    migration_name = '0001_test.py'

    def setUp(self):
        path = get_package_migrations_directory(self.python_path_to_test_package)
        create_migration_file(path, self.migration_name)

    def tearDown(self):
        self._remove_test_migrations_directory()

    def test_correct_result(self):
        path, name = get_migration_python_path_and_name(self.migration_name, self.python_path_to_test_package)
        self.assertEqual(name, self.migration_name.replace('.py', ''))
        self.assertEqual(path, '.'.join((self.python_path_to_test_package, 'migrations', name)))
