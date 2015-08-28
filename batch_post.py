# -*- coding: utf-8 -*-
# import socks
# import socket
# socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 1080)
# socket.socket = socks.socksocket

import os,sys
import random
import logging
import logging.config
import time
from hashlib import md5

import beanstalkc
import MySQLdb
import yaml

import codecs
import handlers
import rap

# 1 2 3 4 5 6 7 8 9 10 11 12 13 18 22

def db_connect():
    """数据库连接

    @return:            connection
    @rtype:             MySQLdb.connections.Connection
    """
    return MySQLdb.connect('192.168.8.55','root','123456','comment',charset='utf8')

def main(dir, date):
    if len(sys.argv) < 2:
        print '缺少参数'
        return
    # 连接数据库
    conn = db_connect()
    cursor = conn.cursor()
    # 第一个参数为site_id
    site_id = sys.argv[1] 
    # 第二个参数非空则为日期
    if len(sys.argv) == 3:
        date = sys.argv[2]
    # 读取site_url, site_name
    cursor.execute('select site_url, site_name from site where site_id = "' + site_id  + '"')
    cur = cursor.fetchall()[0]
    print cur
    if len(cur) == 0:
        print '参数1：site_id不存在'
        return
    post_url, site_name = cur

    titles = os.listdir(dir+date)

    # 保存本地结果的文件夹
    article_url_dir = dir+'article_url/'+date+'/'
    if not os.path.exists(article_url_dir):
        os.mkdir(article_url_dir)

    f = codecs.open(article_url_dir + site_name+'.txt','w', 'utf-8')
    # 读取账号
    cursor.execute('select site_sign, username, password from account_post where site_id = "' + site_id  + '"')
    cur = cursor.fetchall()

    print site_name.encode('utf8'), '账号数:', len(cur)

    for i in range(len(titles)):
    # for i in range(1):
        if i<9:
            t = '00'+str(i+1)
        elif i<99:
            t = '0'+str(i+1)
        else:
            t = str(i+1)

        tid = 'Hong_'+date+'_'+t
        print tid, dir.encode('utf8')+date+'/'+titles[i].encode('utf8')[:-4],

        site_sign, username, password = cur[i%(len(cur))]
        print site_sign.encode('utf8'), username.encode('utf8'), password.encode('utf8')

        c = open(dir+date+'/'+titles[i]).read()
        try:
            content = c.decode('utf8').encode('utf8')
        except:
            content = c.decode('gbk').encode('utf8')

        article_url, log = rap.post(post_url, {'username': username.encode('utf8'),
                                                 'password': password.encode('utf8'),
                                                 'subject': titles[i].encode('utf8')[:-4],
                                                 'content': content})

       
        line = tid + '\t' + site_name + '\t' + titles[i][:-4] + '\t' + article_url
        print line.encode('utf8')
        f.write(line+'\n')
        if article_url != '':   
            sql = 'insert into posts (urlmd5, tid, site_id, title, url, post_time) values (%s, %s, %s, %s, %s, now())'
            urlmd5 = md5(article_url).hexdigest()
            param = (urlmd5, tid, site_id, titles[i][:-4], article_url)
            cursor.execute(sql, param)
            conn.commit()
            time.sleep(60*10)

    f.close()
    cursor.close()
    conn.close()


if __name__ == '__main__':
    # Load local configurations.
    CONFIG = yaml.load(open('config.yaml'))
    # Logging config.
    logging.config.dictConfig(CONFIG)

    dir = u'正能量/'
    date = str(time.strftime("%Y-%m-%d"))

    main(dir, date)