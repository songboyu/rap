# -*- coding: utf-8 -*-
import random
import time
import json
import logging
import logging.config

import MySQLdb
import beanstalkc
import yaml

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
def get_site_sign(post_url):
    """获取URL特征

    @param post_url:    帖子地址
    @type post_url:     str

    @return:            URL特征
    @rtype:             str
    """
    domain = post_url.split('/')[2]
    return domain.split('.')[-2]

def auto_reply():
    try:
        # 连接beanstalkc服务器
        bean = beanstalkc.Connection(CONFIG['beanstalk']['ip'],
                                     CONFIG['beanstalk']['port'])
        bean.use('rap_server')
        bean.ignore('default')
    except:
        logging.critical('Cann\'t connect to beanstalk server')
        return

    try:
        # 连接数据库
        conn = db_connect()

        cursor_get_accounts = conn.cursor()
        cursor_get_accounts.execute('select username,password,site_sign from account where site_sign="倍可亲"')

        cursor_get_contents = conn.cursor()
        cursor_get_contents.execute('select * from man_made_content')

        contents = cursor_get_contents.fetchall()
        contents_counts = cursor_get_contents.rowcount

        for account in cursor_get_accounts.fetchall():
            site_sign = account[2]

            cursor_get_titles = conn.cursor()
            cursor_get_titles.execute('select * from forum_title where instr(website_name,"'+site_sign+'") > 0 and time > date_sub(now(), interval 1 day)')

            titles = cursor_get_titles.fetchall()
            titles_count = cursor_get_titles.rowcount

            for i in range(0, 10):
                print site_sign
                row = titles[random.randint(0, titles_count-1)]
                post_url = row[7]
                website_name = row[4]

                cursor = conn.cursor()
                content = contents[random.randint(0, contents_counts-1)][2]
                sql = 'insert into reply_job (username,password,site_name,content,url,reply_time,mode) values (%s, %s, %s, %s, %s, now(), 1)'
                param = (account[0], account[1], website_name, content, post_url)
                cursor.execute(sql, param)
                conn.commit()

                data = {
                    'job_id':cursor.lastrowid,
                    'post_url':post_url,
                    'mode':'1',
                    'src':{
                        'username':account[0].encode('utf8'),
                        'password':account[1].encode('utf8'),
                        'content':content.encode('utf8'),
                        'nickname':'',
                        'subject':'',
                        'proxies':''
                    }
                }
                logging.info(data)
                bean.put(json.dumps(data))
                time.sleep(15)

        cursor_get_accounts.close()
        cursor_get_contents.close()
        cursor_get_titles.close()
        conn.close()
    except MySQLdb.Error,e:
        logging.critical("Mysql Error %d: %s" % (e.args[0], e.args[1]))

if __name__ == '__main__':
    # Load local configurations.
    CONFIG = yaml.load(open('config.yaml'))
    # Logging config.
    logging.config.dictConfig(CONFIG)
    
    auto_reply()

