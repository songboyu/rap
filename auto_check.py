# -*- coding: utf-8 -*-

import random
import logging
import logging.config

import yaml
import MySQLdb

import rap

def db_connect():
    """数据库连接

    @return:            connection
    @rtype:             MySQLdb.connections.Connection
    """
    return MySQLdb.connect(CONFIG['db']['ip'],
                           CONFIG['db']['username'],
                           CONFIG['db']['password'],
                           CONFIG['db']['dbname'],
                           charset='utf8')

def get_water():
    if 'WATERS' not in globals():
        global WATERS
        WATERS = []
    
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute('SELECT text FROM waters')
        for row in cursor.fetchall():
            WATERS.append(row[0].encode('utf8'))
        conn.close()

    return random.choice(WATERS)

def get_account(url):
    if 'ACCOUNTS' not in globals():
        global ACCOUNTS
        ACCOUNTS = []

        pass

    pass

def get_url():
    pass

def main():
    print get_water().decode('utf8').encode('gbk')

if __name__ == '__main__':
    # Load local configurations.
    CONFIG = yaml.load(open('config.yaml'))
    # Logging config.
    logging.config.dictConfig(CONFIG)

    main()
