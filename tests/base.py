# -*- coding: utf-8 -*-

from os.path import dirname, abspath, join, exists
from shutil import rmtree

from unittest import TestCase


__all__ = (
    'BaseTestCase',
)


class BaseTestCase(TestCase):

    file_system_path_to_test_package = join(dirname(abspath(__file__)), 'test_package')
    file_system_test_migrations_path = join(file_system_path_to_test_package, 'migrations')
    file_system_path_to_init_py_in_migrations_directory = join(file_system_test_migrations_path, '__init__.py')
    python_path_to_test_package = 'tests.test_package'

    def _remove_test_migrations_directory(self):
        if exists(self.file_system_test_migrations_path):
            rmtree(self.file_system_test_migrations_path)
