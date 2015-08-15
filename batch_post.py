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

import beanstalkc
import MySQLdb
import yaml

import codecs
import handlers
import rap

site_name_map = {
        # '1': ('加国华人网','http://bbs.1dpw.com/forum-71-1.html'),
        # '6': ('超级苹果','http://bbs.powerapple.com/forum.php?mod=forumdisplay&fid=50'),
        # '11': ('加拿大家园','http://forum.iask.ca/forums/%E6%B8%A9%E5%93%A5%E5%8D%8E.14/'),
        # '12': ('谜米','http://forum.memehk.com/forum.php?mod=forumdisplay&fid=60'),
        # '14': ('人在温哥华','http://forum.vanpeople.com/forum.php?mod=forumdisplay&fid=67'),
        # '17': ('六六网','http://www.66.ca/forum.php?mod=forumdisplay&fid=36'),
        # '18': ('倍可亲','http://www.backchina.com/forum/37/index-1.html'),
        # '20': ('纽约华人','http://www.nychinaren.com/f/page_viewforum/f_19.html'),
        # '23': ('澳洲新足迹','https://www.oursteps.com.au/bbs/forum.php?mod=forumdisplay&fid=160'),
        # '4': ('万维','http://bbs.creaders.net/life/'),

        '2': (u'无忧论坛','http://bbs.51.ca/forum-40-1.html'),
        '3': (u'阿波罗论坛','http://bbs.aboluowang.com/forum.php?mod=forumdisplay&fid=4'),
        '5': (u'飞月网论坛','http://bbs.onmoon.com/forum.php?mod=forumdisplay&fid=48'),
        '7': (u'文学城论坛','http://bbs.wenxuecity.com/currentevent/'),
        '9': (u'多维社区','http://blog.dwnews.com/'),
        '10': (u'消息树论坛','http://enewstree.com/discuz/forum.php?mod=forumdisplay&fid=47'),
        '13': (u'温哥华巅峰论坛','http://forum.vanhi.com/forum-38-1.html'),
        '15': (u'天易论坛','http://bbs.wolfax.com/f-42-1.html'),
        '16': (u'加易论坛','http://ieasy5.com/bbs/thread.php?fid=3'),
        '19': (u'天涯信息论坛','http://www.myca168.com/bbs/index/thread/id/9'),
        '21': (u'泰国华人论坛','http://www.taihuabbs.com/thread-htm-fid-130.html'),
        '22': (u'外来客论坛','http://www.wailaike.net/group_post?gid=1'),
    }

def db_connect():
    """数据库连接

    @return:            connection
    @rtype:             MySQLdb.connections.Connection
    """
    return MySQLdb.connect('192.168.8.55','root','123456','eventdb',charset='utf8')

def main(dir, date):
    if len(sys.argv) < 2 or sys.argv[1] not in site_name_map:
        print u'参数错误'
        return
    conn = db_connect()
    cursor = conn.cursor()

    titles = os.listdir(dir+date)

    site_id = sys.argv[1] 

    site_name, post_url = site_name_map[site_id]

    f = codecs.open(dir+'article_url/'+date+'/'+site_name+'.txt','w', 'utf-8')

    cursor.execute('select site_sign, username, password from account where site_id = "' + site_id  + '"')
    cur = cursor.fetchall()

    print site_name, u'账号数:', len(cur)

    for i in range(len(titles)):
        if i<10:
            t = '00'+str(i)
        elif i<100:
            t = '0'+str(i)
        else:
            t = str(i)

        tid = 'Hong_'+date+'_'+t
        print tid, dir+date+'/'+titles[i][:-4],

        site_sign, username, password = cur[i%(len(cur))]
        print site_sign, username, password

        article_url, log = rap.post(post_url, {'username': username.encode('utf8'),
                                                 'password': password.encode('utf8'),
                                                 'subject': titles[i].encode('utf8')[:-4],
                                                 'content': open(dir+date+'/'+titles[i]).read()})

       
        line = tid + '\t' + site_name + '\t' + titles[i][:-4] + '\t' + article_url
        print line
        f.write(line+'\n')
        if article_url!= '':
            time.sleep(60)

    f.close()
    cursor.close()
    conn.close()


if __name__ == '__main__':
    
    # Load local configurations.
    CONFIG = yaml.load(open('config.yaml'))
    # Logging config.
    logging.config.dictConfig(CONFIG)

    dir = u'I:/work/正能量/'
    date = '2015-8-14'

    main(dir, date)