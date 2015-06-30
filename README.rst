.. image:: https://travis-ci.org/ts-taiye/raw-sql-migrate.svg?branch=master
    :target: https://travis-ci.org/ts-taiye/raw-sql-migrate

.. image:: https://coveralls.io/repos/ts-taiye/raw-sql-migrate/badge.svg?branch=master
  :target: https://coveralls.io/r/ts-taiye/raw-sql-migrate?branch=master



Goal
====
Raw-sql-migrate is tool for managing your raw SQL migrations.


Docs
====
See <http://rsm.readthedocs.org/en/latest/> page for full docs.


Short guide
===========
1. Create rsm.yaml or rsm.py in your project dir with next structure:

.. code-block:: yaml

    database:
        engine: engine backend module
        host: database host
        port: database port
        name: database name
        user: user name
        password: user password
    history_table_name: migration history table name

.. code-block:: python

    RSM_CONFIG = {
        'database': {
            'engine': engine backend module,
            'host': database host,
            'port': database port,
            'name': database name,
            'user': user name,
            'password': user password,
        },
        'history_table_name': migration history table name,
        'packages': [
            'package_a',
            'package_b',
            'package_c.package_d',
        ],
    }


2. Create first migration

.. code-block:: shell

    rsm create package_a.package_b initial

3. Edit migration file found package_a/package_b/migrations/0001_initial.py. Example:

.. code-block:: python

    def forward(database_api):
        database_api.execute(
            '''
            CREATE TABLE test (
               id INT PRIMARY KEY NOT NULL,
               test_value BIGINT NOT NULL,
            );
            CREATE INDEX test_value_index ON test(test_value);
            '''
        )

    def backward(database_api):
        database_api.execute('DROP TABLE test;')

4. Run migrations:

.. code-block:: shell

    rsm migrate package_a.package_b

5. Migrating backwards:

.. code-block:: shell

    rsm migrate package_a.package_b 0
