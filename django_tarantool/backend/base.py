"""
Tarantool database backend for Django.

Requires python-tarantool: http://github.com/
"""


from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.utils import (
    CursorDebugWrapper as BaseCursorDebugWrapper,
)

import tarantool.dbapi

# Some of these import psycopg2, so import them after checking if it's installed.
from .client import DatabaseClient                          # NOQA isort:skip
from .creation import DatabaseCreation                      # NOQA isort:skip
from .features import DatabaseFeatures                      # NOQA isort:skip
from .introspection import DatabaseIntrospection            # NOQA isort:skip
from .operations import DatabaseOperations                  # NOQA isort:skip
from .schema import DatabaseSchemaEditor                    # NOQA isort:skip


Database = tarantool.dbapi.Connection


class DatabaseWrapper(BaseDatabaseWrapper):
    def is_usable(self):
        return True

    vendor = 'tarantool'
    display_name = 'Tarantool'
    Database = Database
    SchemaEditorClass = DatabaseSchemaEditor
    client_class = DatabaseClient
    creation_class = DatabaseCreation
    features_class = DatabaseFeatures
    introspection_class = DatabaseIntrospection
    ops_class = DatabaseOperations

    data_types = {
        'AutoField': 'INTEGER',
        'BigAutoField': 'INTEGER',
        'BinaryField': 'VARBINARY',
        'BooleanField': 'BOOLEAN',
        'NullBooleanField': 'BOOLEAN',
        'CharField': 'VARCHAR(%(max_length)s)',
        'TextField': 'TEXT',
        'UUIDField': 'VARCHAR(32)',
        'SlugField': 'VARCHAR(%(max_length)s)',
        'DateField': 'UNSIGNED',
        'DateTimeField': 'UNSIGNED',
        'TimeField': 'UNSIGNED',
        'DurationField': 'INTEGER',
        'OneToOneField': 'INTEGER',
        'FileField': 'VARCHAR(%(max_length)s)',
        'FilePathField': 'VARCHAR(%(max_length)s)',
        'BigIntegerField': 'INTEGER',
        'IntegerField': 'INTEGER',
        'PositiveIntegerField': 'UNSIGNED',
        'SmallIntegerField': 'INTEGER',
        'PositiveSmallIntegerField': 'UNSIGNED',
        'FloatField': 'NUMBER',
        'DecimalField': 'NUMBER',
        'IPAddressField': 'VARCHAR(15)',
        'GenericIPAddressField': 'VARCHAR(39)',
    }

    data_types_suffix = {
        'AutoField': 'AUTOINCREMENT',
        'BigAutoField': 'AUTOINCREMENT',
    }

    operators = {
        'exact': '= %s',
        'iexact': '= UPPER(%s)',
        'contains': 'LIKE %s',
        'icontains': 'LIKE UPPER(%s)',
        'regex': '~ %s',
        'iregex': '~* %s',
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',
        'startswith': 'LIKE %s',
        'endswith': 'LIKE %s',
        'istartswith': 'LIKE UPPER(%s)',
        'iendswith': 'LIKE UPPER(%s)',
    }

    def get_connection_params(self):
        settings_dict = self.settings_dict
        # None may be used to connect to the default 'postgres' db

        conn_params = {
            **settings_dict['OPTIONS'],
        }
        conn_params.pop('isolation_level', None)
        if settings_dict['USER']:
            conn_params['user'] = settings_dict['USER']
        if settings_dict['PASSWORD']:
            conn_params['password'] = settings_dict['PASSWORD']
        if settings_dict['HOST']:
            conn_params['host'] = settings_dict['HOST']
        if settings_dict['PORT']:
            conn_params['port'] = settings_dict['PORT']
        return conn_params

    def get_new_connection(self, conn_params):
        connection = Database(**conn_params)
        return connection

    def _set_autocommit(self, value):
        self.connection.autocommit = value

    def init_connection_state(self):
        return True

    def create_cursor(self, name=None):
        return self.connection.cursor()

    def make_debug_cursor(self, cursor):
        return CursorDebugWrapper(cursor, self)


class CursorDebugWrapper(BaseCursorDebugWrapper):
    def copy_expert(self, sql, file, *args):
        with self.debug_sql(sql):
            return self.cursor.copy_expert(sql, file, *args)

    def copy_to(self, file, table, *args, **kwargs):
        with self.debug_sql(sql='COPY %s TO STDOUT' % table):
            return self.cursor.copy_to(file, table, *args, **kwargs)