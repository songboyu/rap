# -*- coding: utf-8 -*-

import socks
import socket
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 1080)
socket.socket = socks.socksocket

import yaml
import requests
import MySQLdb

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
    # conn = MySQLdb.connect('192.168.8.34', 'root', '123456', 'eventdb', charset='utf8')
    cursor = conn.cursor()

    cursor.execute('select id, site_sign, head_image from account')
    for row in cursor.fetchall():
        uid, site_sign, head_image = row
        if site_sign in [u'阿波罗', u'文学城', u'天易', u'无忧', u'谜米', u'加易', u'倍可亲']: continue
        # if site_sign != u'加易': continue

        resp = requests.get(head_image)
        with open('local_head/' + str(uid) + '.jpg', 'wb') as f:
            f.write(resp.content)
        print uid, 'head OK'
        


if __name__ == '__main__':
    # Load local configurations.
    CONFIG = yaml.load(open('config.yaml'))

    main()
