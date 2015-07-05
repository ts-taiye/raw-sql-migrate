# -*- coding: utf-8 -*-

from mock import Mock, patch, call

from tests.base import DatabaseTestCase

from raw_sql_migrate.cli import (
    create, status, migrate, STATUS_HEADER_STRING, AFTER_STATUS_HEADER_STRING, NO_MIGRATION_STRING,
)

from raw_sql_migrate.helpers import FileSystemHelper


class CliTestCase(DatabaseTestCase):

    def setUp(self):
        config = 'rsm.yaml'
        self.create_args = Mock()
        self.create_args.config = config
        self.create_args.name = 'initial'
        self.create_args.package = self.python_path_to_test_package

        self.status_args = Mock()
        self.status_args.config = config
        self.status_args.package = None

        self.migrate_args = Mock()
        self.migrate_args.config = config
        self.migrate_args.package = self.python_path_to_test_package
        self.migrate_args.migration_number = None
        self.patcher = patch('raw_sql_migrate.cli._get_api', new=lambda config_path: self.api)
        self.patcher.start()

    def tearDown(self):
        super(CliTestCase, self).tearDown()
        self.patcher.stop()

    def test_create(self):
        self.assertFalse(FileSystemHelper.get_migrations_list(self.python_path_to_test_package))
        create(self.create_args)
        migrations_list = FileSystemHelper.get_migrations_list(self.python_path_to_test_package)
        self.assertTrue(migrations_list)

    def test_status(self):
        self.status_args.package = None
        with patch('raw_sql_migrate.sys.stdout.write') as write:
            status(self.status_args)
        self.assertTrue(write.called)
        write.assert_called_with(NO_MIGRATION_STRING)

    def test_status_with_migration(self):
        create(self.create_args)
        migrate(self.migrate_args)
        with patch('raw_sql_migrate.sys.stdout.write') as write:
            status(self.status_args)
        self.assertTrue(write.called)
        first_call = call(STATUS_HEADER_STRING)
        second_call = call(AFTER_STATUS_HEADER_STRING)
        write.assert_has_calls((first_call, second_call, ), any_order=True)
