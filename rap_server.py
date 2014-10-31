# -*- coding: utf-8 -*-
"""RAP Server（beanstalkc version）

@author: HSS
@since: 2014-10-229
@summary: RAP Server

"""
import json
import logging
import logging.config

import beanstalkc
import MySQLdb
import yaml
import requests
from bs4 import BeautifulSoup

import rap

def get_url_title(post_url):
    """Get url title with utf8 encoding format.

    @param post_url:    帖子地址
    @type post_url:     str

    @return:            帖子标题
    @rtype：            str
    """
    try:
        resp = requests.get(post_url)
        soup = BeautifulSoup(resp.content)
        title = soup.find('title').text.encode('utf8')
        return title
    except:
        return ''

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

def reply(job_body):
    """回复帖子，并将信息记录到数据库中

    @param job_body:    beanstalk获取的内容
    @type job_body:     json

    """
    src = job_body['src']
    job_id = job_body['job_id']
    post_url = job_body['post_url']

    # 获取帖子标题
    url_title = get_url_title(post_url)

    # 连接数据库
    conn = db_connect()
    cursor = conn.cursor()

    # 将beanstalkc队列中获取到的信息记录到数据库中
    # 将初始状态（status）置为 1 --- 正在发送
    cursor.execute('set character set "utf8"')
    cursor.execute('update reply_job set status = 1, url_title = %s where job_id = %s', (url_title, job_id))
    
    # 将 "正在发送" 状态提交
    conn.commit()
    
    # 调用回复函数
    r, log = rap.reply(post_url, src)

    # 判断回复结果状态
    # 2 --- OK
    # 3 --- Error.
    status = 2 if r else 3
    cursor.execute('update reply_job set status = %s, error = %s, update_time = now() where job_id = %s',
                   (status, log, job_id))
    # 将 "发送成功" 或 "发送失败" 状态提交
    conn.commit()
    # 如果登录失败，将账号状态置为无效
    if 'Login Error' in log:
        # Set the is_invalid tag of this account.
        cursor.execute('update account set is_invalid = 1 '
                       'where username = %(username)s and site_sign in (select site_sign from site where site_url like %s)',
                       (src, '%' + get_site_sign(post_url) + '%'))
    # 提交账号状态
    conn.commit()
    conn.close()

def _decode_dict(data):
    """json.loads()返回编码由unicode转换为utf8

    @param data:    json源数据
    @type data:     str

    @return:        json编码后数据
    @rtype:         json(utf8)
    """
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv

def main():
    """Main eventloop."""
    try:
        # 连接beanstalkc服务器
        bean = beanstalkc.Connection(CONFIG['beanstalk']['ip'],
                                     CONFIG['beanstalk']['port'])
        # 监听rap_server
        bean.watch('rap_out')
        bean.ignore('default')
    except:
        logging.critical('Cann\'t connect to beanstalk server')
        return
    while True:
        # 开启守护进程，持续接收信息
        job = bean.reserve()
        logging.info(job.body)
        try:
            # job_body转为json格式
            job_body = json.loads(job.body, object_hook=_decode_dict)

            logging.info(job_body)
            logging.info('load json ok')

            reply(job_body)
        except:
            logging.exception('reply exception')
            job.release()
        finally:
            job.delete()

if __name__ == '__main__':
    # Load local configurations.
    CONFIG = yaml.load(open('config.yaml'))
    # Logging config.
    logging.config.dictConfig(CONFIG)

    main()
