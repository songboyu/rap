# -*- coding: utf-8 -*-
"""Update acount info in the db.

@author: sniper
@since: 2015-01-30
"""

import socks
import socket
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 1080)
socket.socket = socks.socksocket

import os
import random
import logging
import logging.config

import beanstalkc
import MySQLdb
import yaml

import handlers


def get_account_handler(site_sign):

    site_sign_map = {
        '文学城': handlers.upload_head_wenxuecity_blog,
        '无忧': handlers.upload_head_51_forum,
        '天易': handlers.upload_head_wolfax_forum,
        # '温哥华': handlers.upload_head_vanhi_forum,
        '谜米': handlers.upload_head_memehk_forum,
        '阿波罗': handlers.upload_head_aboluowang_forum,
        '倍可亲': handlers.upload_head_backchina_forum,
    }
    if site_sign in site_sign_map:
        return site_sign_map[site_sign]
    else:
        return None

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


def main():
    conn = db_connect()
    cursor = conn.cursor()

    heads = os.listdir('head')

    cursor.execute('select id, site_sign, username, password from account')
    for row in cursor.fetchall():
        uid, site_sign, username, password = row

        site_sign = site_sign.encode('utf8')
        account_handler = get_account_handler(site_sign)
        if not account_handler: continue

        print site_sign.decode('utf8'), account_handler
        print username, password

        try:
            head_url, log = account_handler({'username': username,
                                             'password': password,
                                             'head': 'head/' + random.choice(heads),
                                             'TTL': 3,
                                             'proxies': ''})
        except:
            logging.exception('Upload head Error')
            continue
        if head_url == '': continue

        # cursor.execute('update account set head_image=%s where id=%s', (head_url, uid))
        # conn.commit()

    cursor.close()
    conn.close()


if __name__ == '__main__':
    # Load local configurations.
    CONFIG = yaml.load(open('config.yaml'))
    # Logging config.
    logging.config.dictConfig(CONFIG)

    main()


