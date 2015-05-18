# -*- coding: utf-8 -*-

from os.path import dirname, abspath, join, exists, realpath
from shutil import rmtree

from unittest import TestCase

from raw_sql_migrate import Config
from raw_sql_migrate.api import Api


__all__ = (
    'BaseTestCase',
    'DatabaseTestCase',
)


class BaseTestCase(TestCase):

    file_system_path_to_test_package = join(dirname(abspath(__file__)), 'test_package')
    file_system_test_migrations_path = join(file_system_path_to_test_package, 'migrations')
    file_system_path_to_init_py_in_migrations_directory = join(file_system_test_migrations_path, '__init__.py')
    python_path_to_test_package = 'tests.test_package'
    config = None
    api = None

    def _remove_test_migrations_directory(self):
        if exists(self.file_system_test_migrations_path):
            rmtree(self.file_system_test_migrations_path)

    def tearDown(self):
        self._remove_test_migrations_directory()


class DatabaseTestCase(BaseTestCase):

    def setUp(self):
        self.config = Config().init_from_file(join(dirname(realpath(__file__)), 'test_config.yaml'))
        self.api = Api(self.config)
