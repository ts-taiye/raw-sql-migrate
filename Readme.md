[![Build Status](https://travis-ci.org/ts-taiye/raw-sql-migrate.svg?branch=master)](https://travis-ci.org/ts-taiye/raw-sql-migrate)
[![Coverage Status](https://coveralls.io/repos/ts-taiye/raw-sql-migrate/badge.svg)](https://coveralls.io/r/ts-taiye/raw-sql-migrate)

## Goal
Raw-sql-migrate is replacement for South migration system without ORM using raw sql. 

## TODO
- Write tests.
- Make database backend support for MySQL, Oracle Database.
- Make base consistency check.

## Usage
In order to use migrate api use should make an instance of Api class found in raw_sql_migrate.api module.
It receives config instance as required param. There are two ways to get config:
- Provide your own instance of Config class found in raw_sql_migrate package
- Create raw_sql_migrate.yaml somewhere on your path with next structure:
```yaml
database:
    host: database host
    port: database port
    name: database name
    user: user name
    password: user password

history_table_name: migration history table name
```

### Creating new migration
In order to create new migration just call create method:
```python
api.create(package='package_a.package_b', name='initial')
```
Calling of it will create new migrations history table,
migrations directory in the package and py migration file

### Migrating forward
In order to migrate forward call
```python
api.forward(package, migration_number=42)
```
Note: to migrate all not applied migrations you should skip migration_number param.

### Migrating backward
In order to migrate forward call
```python
api.backward(package, migration_number=1)
```
Note: to migrate to zero state you should pass migration_number as 0.

## Migration file
Migration file is usual python file with two predefined functions:
forward and backward. Database api instance is passed to them.
In order to use call raw sql command just call database_api.execute method.

## Transaction control
Each migration is executed in separate transaction which will be 
commited after all python code in forward or backward is executed.
Still you can commit transaction yourself. Just pass commit=True to
execute method of database api.


