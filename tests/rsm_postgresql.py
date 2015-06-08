# -*- coding: utf-8 -*-

RSM_CONFIG = {
    'database': {
        'engine': 'raw_sql_migrate.engines.postgresql_psycopg2',
        'host': '',
        'port': '',
        'name': 'rsm_test',
        'user': 'postgres',
        'password': '',
    },
    'history_table_name': 'migration_history',
    'packages': [
        'tests.test_package',
    ],
}
