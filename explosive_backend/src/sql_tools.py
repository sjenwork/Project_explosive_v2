from sqlalchemy import create_engine
from configparser import ConfigParser
import socket
import os
from urllib.parse import quote
import pyodbc as sqldriver


config = ConfigParser()
config.read('src/conf.ini')
print(list(config.items()))


def get_conn(machineName, name=None):
    if name:
        print(f'  >> call dbconnection method from {name}')
    hostname = socket.gethostname()

    server = config[machineName]['sql_server']
    port = config[machineName]['sql_port']
    table = config[machineName]['sql_table']
    username = config[machineName]['sql_username']
    password = quote(config[machineName]['sql_password'])
    sqlalchemy_driver = config[machineName]['sql_sqlalchemy_driver']
    # info = f'''DRIVER={driver};SERVER={server};UID={username};PWD={password}'''

    conn = 'mssql+pymssql://username:password@server:port/table'
    if hostname == 'JenMBP.local':
        conn = 'mssql+pyodbc://username:password@server:port/table?driver=sqlalchemy_driver'
    conn = (conn
            .replace('username', username)
            .replace('server', server)
            .replace('port', port)
            .replace('table', table)
            .replace('username', username)
            .replace('password', password)
            .replace('sqlalchemy_driver', sqlalchemy_driver)
            )
    engine = create_engine(conn)
    return engine


def table_check(tablename, machineName):
    with open(f'src/sql/{tablename}.sql') as f:
        sql = f.read()

    cnxn = get_conn(machineName)
    cursor = cnxn.cursor(machineName)
    cursor.execute(sql)
    cnxn.commit()


def insert(elem, tablename, machineName):
    table_check(tablename, machineName)
    cnxn = get_conn(machineName)
    cursor = cnxn.cursor()
    sql = '''
    insert into TABLE(COLUMNS) values(VALUES)
    '''
    sql2 = (
        sql
        .replace('TABLE', tablename)
        .replace('COLUMNS', ','.join(elem.keys()))
        .replace('VALUES', ','.join(['?' for i in elem.keys()]))
        .replace('\n', '')
        .replace('"', "'")
    )
    # print(list(elem.values()))
    cursor.execute(sql2, list(elem.values()))
    cnxn.commit()


def fetchall(sql, machineName):
    cnxn = get_conn(machineName)
    cursor = cnxn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()


def alter(sql):
    '''
    ALTER TABLE explosive_rawdata 
    ADD IsMerge [bit] NOT NULL DEFAULT 0
    '''
    cnxn = get_conn()
    cursor = cnxn.cursor()
    cursor.execute(sql)
