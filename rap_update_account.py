# -*- coding: utf-8 -*-
"""Update acount info in the db.

@author: sniper
@since: 2015-01-30
"""

import socks
import socket
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 1080)
socket.socket = socks.socksocket

import logging
import logging.config

import beanstalkc
import MySQLdb
import yaml

import handlers


def get_account_handler(site_sign):
    site_sign_map = {
        # '凯迪': handlers.get_account_info_kdnet,
        # '文学城': handlers.get_account_info_wenxuecity_blog,
        # '无忧': handlers.get_account_info_51_forum,
        # '加易': handlers.get_account_info_ieasy5_forum,
        # '天易': handlers.get_account_info_wolfax_forum,
        # '温哥华': handlers.get_account_info_vanhi_forum,
        # '谜米': handlers.get_account_info_memehk_forum,
        # '消息树': handlers.get_account_info_enewstree_forum,
        # '超级苹果': handlers.get_account_info_powerapple_forum,
        # '外来客': handlers.get_account_info_wailaike_forum,
        # '新浪': handlers.get_account_info_sina_club,
        # '欧浪': handlers.get_account_info_eulam_forum,
        # '加国华人网': handlers.get_account_info_1dpw_forum,
        # '多维': handlers.get_account_info_dwnews_blog,
        # '阿波罗': handlers.get_account_info_aboluowang_forum,
        # '倍可亲': handlers.get_account_info_backchina_forum,
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

    cursor.execute('set names utf8')
    cursor.execute('select id, site_sign, username, password from account')
    for row in cursor.fetchall():
        uid, site_sign, username, password = row

        site_sign = site_sign.encode('utf8')
        account_handler = get_account_handler(site_sign)
        if not account_handler: continue

        print site_sign.decode('utf8'), account_handler
        print username, password
        
        try:
            info, log = account_handler({'username': username, 'password': password, 'TTL': 3, 'proxies': ''})
        except:
            logging.exception('Get account info Error')
            continue
        if info == {}: continue
        params = {'uid': uid}
        params.update(info)
        sql_str = ('update account set '
                   'head_image = %(head_image)s, '
                   'account_score = %(account_score)s, '
                   'account_class = %(account_class)s, '
                   'time_register = %(time_register)s, '
                   'time_last_login = now(), '
                   'login_count = %(login_count)s, '
                   'count_post = %(count_post)s, '
                   'count_reply = %(count_reply)s '
                   'where id=%(uid)s')
        cursor.execute(sql_str, params)
        conn.commit()

    cursor.close()
    conn.close()


if __name__ == '__main__':
    # Load local configurations.
    CONFIG = yaml.load(open('config.yaml'))
    # Logging config.
    logging.config.dictConfig(CONFIG)

    main()
