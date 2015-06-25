# -*- coding: utf-8 -*-

import sys

from raw_sql_migrate import Config, ConfigNotFoundException
from raw_sql_migrate.api import Api


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

    result = api.status(package=args.package)  # config=rsm_config
    if not result:
        sys.stdout.write('No migration history found.\n')
        return
    sys.stdout.write('%-40s %-40s %-40s \n' % (u'package', u'name', u'processed_at', ))
    sys.stdout.write('%s \n' % (u'-' * 120))
    for package in result:
        sys.stdout.write(
            '%-40s %-40s %-40s \n' % (package, result[package]['name'], result[package]['processed_at'], )
        )


def create(args):

    api = _get_api(config_path=args.config)

    if not api:
        return

    migration_name = api.create(package=args.package, name=args.name)

    sys.stdout.write('%s migration was created for %s package\n' % (migration_name, args.package))
