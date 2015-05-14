# -*- coding: utf-8 -*-

from unittest import TestCase
from raw_sql_migrate.helpers import generate_migration_name, MIGRATION_NAME_TEMPLATE, DIGITS_IN_MIGRATION_NUMBER


__all__ = (
    'TestGenerateMigrationName',
)


class TestGenerateMigrationName(TestCase):

    def test_positive_case(self):
        name = 'abc'
        self.assertEqual(generate_migration_name(name), '%s_%s.py' % (MIGRATION_NAME_TEMPLATE % 1, name))

    def test_incorrect_number_given(self):
        name = 'abc'
        self.assertRaises(TypeError, generate_migration_name, name, object())
