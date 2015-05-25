## Goal
Raw-sql-migrate is replacement for South migration system without ORM using raw sql. 


## Config
In order to use migrate api use should make an instance of Config class found in raw_sql_migrate package.
By default one config instance is created in raw_sql_migrate.__init__.py module which try to load options
from raw_sql_migrate.yaml in your project root. Still you can create config based on yaml file located in 
another directory. To do it:
```python
from raw_sql_migrate import Config
config = Config().init_from_file(path_to_file)
```
Or you can just pass all params to constructor:
```python
from raw_sql_migrate import Config
config = Config(database, history_table_name)
```
where params are mappings to yaml config structure:
```yaml
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
```
where available options are:
- raw_sql_migrate.engines.postgresql_psycopg2 (requires psycopg2 package)
- raw_sql_migrate.engines.mysql (requires MySQLdb-python package)
Also you can pass specific param to drivers connect method, just add this param in database section.


## Api
In order to create and run migrations you need to make instance of Api class from
raw_sql_migrate.api module and pass config instance if needed. Otherwise default config
will be used.


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

### Migrations status
To get latest migration data for tracked packages call method:
```python
api.status(package='package_a.package_b')
```
In order to get info for all tracked packages just omit package attribute.
The result of this method is python dictionary:
```python
{
    'package name': 
    {
        'name': 'migration name',
        'processed_at': datetime when migration was applied,
    }
}
```

## Migration file
Migration file is usual python file with two predefined functions:
forward and backward. Database api instance is passed to them.
In order to use call raw sql command just call database_api.execute method.

## Transaction control
Each migration is executed in separate transaction which will be 
commited after all python code in forward or backward is executed.
Still you can commit transaction yourself. Just pass commit=True to
execute method of database api.
