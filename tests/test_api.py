# -*- coding: utf-8 -*-

from os.path import exists

from raw_sql_migrate.exceptions import ParamRequiredException
from raw_sql_migrate.helpers import FileSystemHelper
from raw_sql_migrate.engines import database_api_storage

from tests.base import DatabaseTestCase


__all__ = (
    'GenerateMigrationNameTestCase',
    'MigrateForwardTestCase',
    'MigrateBackwardTestCase',
    'StatusTestCase',
)


class GenerateMigrationNameTestCase(DatabaseTestCase):

    test_migration_name = 'test'

    def setUp(self):
        super(GenerateMigrationNameTestCase, self).setUp()

    def test_create_migration(self):
        self.api.create(self.python_path_to_test_package, 'test_migration_name')
        self.assertTrue(exists(self.file_system_test_migrations_path))
        self.assertTrue(exists(self.file_system_path_to_init_py_in_migrations_directory))
        migration_list = FileSystemHelper.get_migrations_list(self.python_path_to_test_package)
        self.assertEqual(len(migration_list), 1)

    def test_no_migration_name_given(self):
        self.assertRaises(ParamRequiredException, self.api.create, '', 'test')
        self.assertRaises(ParamRequiredException, self.api.create, self.python_path_to_test_package, '')

    def test_created_next(self):
        self.api.create(self.python_path_to_test_package, 'test_migration_name')
        self.api.create(self.python_path_to_test_package, 'test_migration_name')
        migration_list = FileSystemHelper.get_migrations_list(self.python_path_to_test_package)
        self.assertEqual(len(migration_list), 2)

    def test_history_table_created(self):
        self.api.create(self.python_path_to_test_package, 'test_migration_name')
        self.assertTrue(self.api.database_helper.migration_history_exists())
#
#
class MigrateForwardTestCase(DatabaseTestCase):

    def setUp(self):
        super(MigrateForwardTestCase, self).setUp()
        self.api.create(self.python_path_to_test_package, 'test_migration_name')

    def tearDown(self):
        self.api.migrate(self.python_path_to_test_package, 0)
        super(MigrateForwardTestCase, self).tearDown()

    def test_migrate_forward(self):
        self.api.migrate(self.python_path_to_test_package)
        self.assertTrue(self.api.database_helper.get_latest_migration_number(self.python_path_to_test_package), 1)

    def test_create_and_forward_two_migrations(self):
        print __name__
        self.api.create(self.python_path_to_test_package, 'test_migration_name2')
        self.api.migrate(self.python_path_to_test_package)
        self.assertTrue(self.api.database_helper.get_latest_migration_number(self.python_path_to_test_package), 2)

    def test_forward_from_packages_config_section(self):
        self.api.migrate()
        self.assertTrue(self.api.database_helper.get_latest_migration_number(self.python_path_to_test_package), 1)


class MigrateBackwardTestCase(DatabaseTestCase):

    def setUp(self):
        super(MigrateBackwardTestCase, self).setUp()
        self.api.create(self.python_path_to_test_package, 'test_migration_name')
        self.api.migrate(self.python_path_to_test_package)

    def tearDown(self):
        super(MigrateBackwardTestCase, self).tearDown()

    def test_migrate_backward(self):
        self.assertTrue(self.api.database_helper.get_latest_migration_number(self.python_path_to_test_package), 1)
        self.api.migrate(self.python_path_to_test_package, 0)
        self.assertEqual(self.api.database_helper.get_latest_migration_number(self.python_path_to_test_package), 0)

class SquashTestCase(DatabaseTestCase):

    def setUp(self):
        super(SquashTestCase, self).setUp()

    def tearDown(self):
        super(SquashTestCase, self).tearDown()

    def test_simple_squash(self):
        for name in ('test1', 'test2', 'test3'):
            self.api.create(self.python_path_to_test_package, name)

        migrations = FileSystemHelper.get_migrations_list(self.python_path_to_test_package)
        self.assertEqual(len(migrations), 3)
        self.api.squash(self.python_path_to_test_package, begin_from=1)
        migrations = FileSystemHelper.get_migrations_list(self.python_path_to_test_package)
        self.assertEqual(len(migrations), 1)
        self.assertTrue(migrations.get(1) is not None)


class StatusTestCase(DatabaseTestCase):

    def setUp(self):
        super(StatusTestCase, self).setUp()
        self.api._create_migration_history_table_if_not_exists()
        self.api.database_helper.write_migration_history('0001_initial', 'test_package')
        database_api_storage.database_api.commit()

    def tearDown(self):
        super(StatusTestCase, self).tearDown()

    def test_correct_status_for_multiple_migrations(self):
        self.api.database_helper.write_migration_history('0002_do_something', 'test_package')
        database_api_storage.database_api.commit()
        data = self.api.status()
        self.assertEqual(len(data.keys()), 1)

    def test_correct_status_for_multiple_migrations_with_package(self):
        self.api.database_helper.write_migration_history('0002_do_something', 'test_package')
        database_api_storage.database_api.commit()
        data = self.api.status(package='test_package')
        self.assertEqual(len(data.keys()), 1)

    def test_single_migration_status(self):
        data = self.api.status()
        self.assertEqual(len(data.keys()), 1)
        self.assertEqual(data['test_package']['name'], '0001_initial')
