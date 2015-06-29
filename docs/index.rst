.. raw-sql-migrate documentation master file, created by
   sphinx-quickstart on Tue Jun 02 23:08:26 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Goal
====
Raw-sql-migrate is tool for managing your raw SQL migrations.


Config
======
To configure database connection you should create a config file in folder, where you will run the migration tool.
The config file can be of .yaml or .py type and by default named `rsm`, but it is not necessary condition, because
every command of rsm accepts --config parameter where you can pass a path to config file.
If path to file is not specified, then rsm.py and rsm.yaml will be searched in the run directory.

Examples of config files:
rsm.yaml:

.. code-block:: yaml

    database:
        engine: engine backend module
        host: database host
        port: database port
        name: database name
        user: user name
        password: user password
        additional_driver_param1: value
        additional_driver_param2: value
    history_table_name: migration history table name
    packages:
        - package_a
        - package_b
        - package_c.package_d

rsm.py:

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

Available options of 'engine' are:

* raw_sql_migrate.engines.postgresql_psycopg2 (requires psycopg2 package)
* raw_sql_migrate.engines.mysql (requires MySQLdb-python package)

Also you can pass specific params to driver connect method, just add them to config database section.
Packages param is a list of packages where to search for new migrations.


Usage
=====

Creating new migration
----------------------
In order to create new migration just call create command

.. code-block:: shell

    rsm create package_a.package_b initial

Calling it will create new migrations history table, migrations directory
in the package_b and 0001_initial.py migration file

Migrating forward
-----------------
In order to migrate forward call

.. code-block:: shell

    rsm migrate package 0003

Note: to migrate all not applied migrations you should skip migration_number param.

Migrating backward
------------------
In order to migrate backward call

.. code-block:: shell

    rsm migrate package 0001

Note: to migrate to initial state you should pass migration_number as 0.

Migrations status
-----------------
To get latest migration data for tracked packages call method:

.. code-block:: shell

    rsm status package_a.package_b

To get info for all tracked packages just omit package name attribute.

.. code-block:: shell

    package                                  name                                     processed_at
    ------------------------------------------------------------------------------------------------------------------------
    package_a.package_b                      0001_initial                             2015-06-25 23:06:56.698562


Squashing migrations
--------------------
Sometimes there can be situation when you want to merge your dev migrations before
publishing them to repository. In this case use squash method:

.. code-block:: shell

    rsm squash package_a.package_b 0042 squashed_migration

This example does next things:
It searches for not applied migration in package begining from number 42, reads their
content and appends it to result forward and backward functions. After all migrations
were processed command writes new migration file with 'begin_from' number and renames
squashed migrations with '_squashed' prefix. Note that command can't squash already
applied migrations.


Transaction Control
-------------------

Each migration runs in separate transaction, which will be started when first sql is executed and committed
when all the code in forward\backward functions is executed. If there is an exception during migrate function all changes
will be rolled back.
