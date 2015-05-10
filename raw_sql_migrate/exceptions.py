# -*- coding: utf-8 -*-

__all__ = (
    'RawSqlMigrateException',
    'InconsistentParamsException',
    'NoNewMigrationsFoundException',
    'IncorrectMigrationFile',
)


class RawSqlMigrateException(Exception):
    pass


class InconsistentParamsException(RawSqlMigrateException):
    pass


class NoNewMigrationsFoundException(RawSqlMigrateException):
    pass


class IncorrectMigrationFile(RawSqlMigrateException):
    pass