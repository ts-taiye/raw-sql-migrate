[![Build Status](https://travis-ci.org/ts-taiye/raw-sql-migrate.svg?branch=master)](https://travis-ci.org/ts-taiye/raw-sql-migrate)
[![Coverage Status](https://coveralls.io/repos/ts-taiye/raw-sql-migrate/badge.svg)](https://coveralls.io/r/ts-taiye/raw-sql-migrate)

## Goal
Raw-sql-migrate is replacement for South migration system without ORM using raw sql. 


## Docs
See [ReadTheDocs](http://rsm.readthedocs.org/en/latest/)  page for full docs.


## TODO
- Write tests.
- Make database backend support for Oracle Database.
- Make base consistency check.


## Short guide
- Create raw_sql_migrate.yaml in your project dir with next structure:
```yaml
database:
    engine: engine backend module
    host: database host
    port: database port
    name: database name
    user: user name
    password: user password
history_table_name: migration history table name
```
- Import and make instance of Api:
```python
from raw_sql_migrate.api import Api
api = Api()
```
- Create first migration
```python
api.create('package_a.package_b', name='initial')
```
- Edit migration file found package_a/package_b/migrations/0001_initial.py. Example:
```python
def forward(database_api):
    database_api.execute(
        sql='''
        CREATE TABLE test (
           id INT PRIMARY KEY NOT NULL,
           test_value BIGINT NOT NULL,
        );
        CREATE INDEX test_value_index ON test(test_value);
        ''',
        params={},
        return_result=None,
    )
    database_api.commit()
def backward(database_api):
    database_api.execute(
        sql='''
        DROP TABLE test;
        ''',
        params={},
        return_result=None,
    )
    database_api.commit()
```
- Run migrations:
```python
api.forward('package_a.package_b')
```
- Migrating backwards:
```python
api.backward('package_a.package_b')
```
