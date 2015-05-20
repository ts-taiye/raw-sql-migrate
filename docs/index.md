## Goal
Raw-sql-migrate is replacement for South migration system without ORM using raw sql. 


## Usage
In order to use migrate api use should make an instance of Api class found in raw_sql_migrate.api module.
It receives config instance as required param. There are two ways to get config:
- Provide your own instance of Config class found in raw_sql_migrate package
- Create raw_sql_migrate.yaml somewhere on your path with next structure:
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
where yet the only available option is:
- raw_sql_migrate.engines.postgresql_psycopg2
- raw_sql_migrate.engines.mysql


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
