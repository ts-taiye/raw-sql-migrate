# -*- coding: utf-8 -*-

__all__ = (
    'RawSqlMigrateException',
    'InconsistentParamsException',
    'NoForwardMigrationsFound',
    'NoBackwardMigrationsFound',
    'IncorrectMigrationFile',
)


class RawSqlMigrateException(Exception):
    pass


class InconsistentParamsException(RawSqlMigrateException):
    pass


class NoForwardMigrationsFound(RawSqlMigrateException):
    pass


class NoBackwardMigrationsFound(RawSqlMigrateException):
    pass


class IncorrectMigrationFile(RawSqlMigrateException):
    pass


class IncorrectPackage(RawSqlMigrateException):
    pass
