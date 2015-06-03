# -*- coding: utf-8 -*-

__all__ = (
    'RawSqlMigrateException',
    'IncorrectDbBackendException',
    'InconsistentParamsException',
    'ParamRequiredException',
    'NoMigrationsFoundToApply',
    'IncorrectMigrationFile',
)


class RawSqlMigrateException(Exception):
    pass


class IncorrectDbBackendException(Exception):
    pass


class InconsistentParamsException(RawSqlMigrateException):
    pass


class ParamRequiredException(RawSqlMigrateException):
    pass


class NoMigrationsFoundToApply(RawSqlMigrateException):
    pass


class IncorrectMigrationFile(RawSqlMigrateException):
    pass


class IncorrectPackage(RawSqlMigrateException):
    pass
