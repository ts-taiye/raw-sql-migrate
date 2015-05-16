# -*- coding: utf-8 -*-

from os.path import exists
from shutil import rmtree

from tests.base import BaseTestCase


__all__ = (
    'TestGenerateMigrationName',
)


class TestGenerateMigrationName(BaseTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        if exists(self.file_system_test_migrations_path):
            rmtree(self.file_system_test_migrations_path)

