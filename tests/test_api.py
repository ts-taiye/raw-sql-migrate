# -*- coding: utf-8 -*-

from os.path import exists

from raw_sql_migrate.api import Api
from raw_sql_migrate.exceptions import ParamRequiredException
from raw_sql_migrate.helpers import get_migrations_list

from tests.base import DatabaseTestCase


__all__ = (
    'TestGenerateMigrationName',
)


class TestGenerateMigrationName(DatabaseTestCase):

    test_migration_name = 'test'

    def setUp(self):
        super(TestGenerateMigrationName, self).setUp()
        self.api = Api(self.config)

    def test_create_migration(self):
        self.api.create(self.python_path_to_test_package, 'test_migration_name')
        self.assertTrue(exists(self.file_system_test_migrations_path))
        self.assertTrue(exists(self.file_system_path_to_init_py_in_migrations_directory))
        migration_list = get_migrations_list(self.python_path_to_test_package)
        self.assertEqual(len(migration_list), 1)

    def test_no_migration_name_given(self):
        self.assertRaises(ParamRequiredException, self.api.create, '', 'test')
        self.assertRaises(ParamRequiredException, self.api.create, self.python_path_to_test_package, '')

    def test_migration_already_exists(self):
        self.api.create(self.python_path_to_test_package, 'test_migration_name')
        self.api.create(self.python_path_to_test_package, 'test_migration_name')
        migration_list = get_migrations_list(self.python_path_to_test_package)
        self.assertEqual(len(migration_list), 1)

    def test_history_table_created(self):
        self.api.create(self.python_path_to_test_package, 'test_migration_name')
        self.assertTrue(self.api.database_helper.migration_history_exists())
