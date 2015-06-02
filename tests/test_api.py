# -*- coding: utf-8 -*-

from os.path import exists

from raw_sql_migrate.api import Api
from raw_sql_migrate.exceptions import ParamRequiredException
from raw_sql_migrate.helpers import get_migrations_list

from tests.base import DatabaseTestCase


__all__ = (
    'GenerateMigrationNameTestCase',
    'MigrateForwardTestCase',
    'MigrateBackwardTestCase',
)


class GenerateMigrationNameTestCase(DatabaseTestCase):

    test_migration_name = 'test'

    def setUp(self):
        super(GenerateMigrationNameTestCase, self).setUp()

    def test_create_migration(self):
        self.api.create(self.python_path_to_test_package, 'test_migration_name')
        self.assertTrue(exists(self.file_system_test_migrations_path))
        self.assertTrue(exists(self.file_system_path_to_init_py_in_migrations_directory))
        migration_list = get_migrations_list(self.python_path_to_test_package)
        self.assertEqual(len(migration_list), 1)

    def test_no_migration_name_given(self):
        self.assertRaises(ParamRequiredException, self.api.create, '', 'test')
        self.assertRaises(ParamRequiredException, self.api.create, self.python_path_to_test_package, '')

    def test_created_next(self):
        self.api.create(self.python_path_to_test_package, 'test_migration_name')
        self.api.create(self.python_path_to_test_package, 'test_migration_name')
        migration_list = get_migrations_list(self.python_path_to_test_package)
        self.assertEqual(len(migration_list), 2)

    def test_history_table_created(self):
        self.api.create(self.python_path_to_test_package, 'test_migration_name')
        self.assertTrue(self.api.database_helper.migration_history_exists())


class MigrateForwardTestCase(DatabaseTestCase):

    def setUp(self):
        super(MigrateForwardTestCase, self).setUp()
        self.api.create(self.python_path_to_test_package, 'test_migration_name')

    def tearDown(self):
        self.api.backward(self.python_path_to_test_package)
        super(MigrateForwardTestCase, self).tearDown()

    def test_migrate_forward(self):
        self.api.forward(self.python_path_to_test_package)
        self.assertTrue(self.api.database_helper.get_latest_migration_number(self.python_path_to_test_package), 1)

    def test_create_and_forward_two_migrations(self):
        self.api.create(self.python_path_to_test_package, 'test_migration_name2')
        self.api.forward(self.python_path_to_test_package)
        self.assertTrue(self.api.database_helper.get_latest_migration_number(self.python_path_to_test_package), 1)

    def test_forward_from_packages_config_section(self):
        self.api.forward()
        self.assertTrue(self.api.database_helper.get_latest_migration_number(self.python_path_to_test_package), 1)


class MigrateBackwardTestCase(DatabaseTestCase):

    def setUp(self):
        super(MigrateBackwardTestCase, self).setUp()
        self.api.create(self.python_path_to_test_package, 'test_migration_name')
        self.api.forward(self.python_path_to_test_package)

    def tearDown(self):
        super(MigrateBackwardTestCase, self).tearDown()

    def test_migrate_backward(self):
        self.assertTrue(self.api.database_helper.get_latest_migration_number(self.python_path_to_test_package), 1)
        self.api.backward(self.python_path_to_test_package)
        self.assertEqual(self.api.database_helper.get_latest_migration_number(self.python_path_to_test_package), 0)


class SquashTestCase(DatabaseTestCase):

    def setUp(self):
        super(SquashTestCase, self).setUp()

    def tearDown(self):
        super(SquashTestCase, self).tearDown()

    def test_simple_squash(self):
        for name in ('test1', 'test2', 'test3'):
            self.api.create(self.python_path_to_test_package, name)

        migrations = get_migrations_list(self.python_path_to_test_package)
        self.assertEqual(len(migrations), 3)
        self.api.squash(self.python_path_to_test_package, begin_from=1)
        migrations = get_migrations_list(self.python_path_to_test_package)
        self.assertEqual(len(migrations), 1)
        self.assertTrue(migrations.get(1) is not None)
