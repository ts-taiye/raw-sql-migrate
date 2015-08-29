# -*- coding: utf-8 -*-

import sys

from raw_sql_migrate import Config, ConfigNotFoundException
from raw_sql_migrate.api import Api
from raw_sql_migrate.exceptions import NoMigrationsFoundToApply, InconsistentParamsException


STATUS_HEADER_STRING = '%-40s %-40s %-40s \n' % (u'package', u'name', u'processed_at', )
AFTER_STATUS_HEADER_STRING = '%s \n' % (u'-' * 120)
STATUS_TEMPLATE_STRING = '%-40s %-40s %-40s \n'
NO_MIGRATION_STRING = 'No migration history found.\n'


def _get_api(config_path=None):
    config = None
    if config_path:
        config = Config()
        try:
            config.init_from_file(config_path)
        except ConfigNotFoundException as e:
            sys.stderr.write(e.message + '\n')
            return None

    return Api(config=config)


def status(args):
    api = _get_api(config_path=args.config)
    if not api:
        return

    result = api.status(package=args.package)
    if not result:
        sys.stdout.write(NO_MIGRATION_STRING)
        return
    sys.stdout.write(STATUS_HEADER_STRING)
    sys.stdout.write(AFTER_STATUS_HEADER_STRING)
    for package in result:
        sys.stdout.write(
            STATUS_TEMPLATE_STRING % (package, result[package]['name'], result[package]['processed_at'], )
        )


def create(args):

    api = _get_api(config_path=args.config)

    if not api:
        return

    migration_name = api.create(package=args.package, name=args.name)

    sys.stdout.write('%s migration was created for %s package\n' % (migration_name, args.package))


def migrate(args):

    api = _get_api(config_path=args.config)

    if not api:
        return

    try:
        api.migrate(package=args.package, migration_number=args.migration_number)
    except (NoMigrationsFoundToApply, InconsistentParamsException) as e:
        sys.stderr.write(e.message + '\n')
    else:
        sys.stdout.write('Done.\n')


def squash(args):

    api = _get_api(config_path=args.config)

    if not api:
        return

    try:
        api.squash(package=args.package, begin_from=args.begin_from, name=args.name)
    except InconsistentParamsException as e:
        sys.stderr.write(e.message + '\n')
    else:
        sys.stdout.write('Done.\n')
