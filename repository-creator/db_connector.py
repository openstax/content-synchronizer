#!/bin/bash

import psycopg2


class DBConnectionException(Exception):
    pass


def connect(host: str = None, port: int = 5432, username: str = None, password: str = None, database: str = None):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host=host, port=port, database=database, user=username, password=password)


    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        raise DBConnectionException(error)
    finally:
        return conn


def pg_close_connection(connection=None):
    if connection is not None:
        connection.close()
        print('Database connection closed.')


def check_pg_version(connection=None):
    if connection:
        cursor = connection.cursor()
        cursor.execute('SELECT version()')
        db_version = cursor.fetchone()
        cursor.close()
        return db_version
    return ''
