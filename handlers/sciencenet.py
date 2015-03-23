# -*- coding: utf-8 -*-
"""科学网社区模块

@author: YMY
@since: 2015-3-23
@summary: 科学网群组

@var CHARSET: 科学网社区网页编码
@type CHARSET: str

"""
import re
import urllib
import time
import binascii

from bs4 import BeautifulSoup

from utils import *

CHARSET = 'gbk'

def login_sciencenet(sess, src):
    """ 科学网登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    # Load login page.
    host = 'http://bbs.sciencenet.cn/'
    resp = sess.get(host + 'forum.php?mod=post&action=newthread&fid=40')
    soup = BeautifulSoup(resp.content)

    form = soup.find('form', attrs={'id': 'lsform'})
    payload = get_datadic(form, CHARSET)
    payload['username'] = src['username']
    payload['password'] = src['password']
    resp = sess.post(host + form['action'] + '&inajax=1', data=payload)
    if src['username'] not in resp.content:
        return False
    return True

def post_sciencenet(post_url, src):
    logger = RAPLogger(post_url)
    sess = RAPSession(src)
    host = 'http://bbs.sciencenet.cn/'

    if not login_sciencenet(sess, src):
        logger.error(' Login Error')
        return ('', str(logger))
    logger.info(' Login OK')

    # Post
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'postform'})
    payload = get_datadic(form, CHARSET)
    payload['subject'] = src['subject'].decode('utf8').encode(CHARSET)
    payload['message'] = src['content'].decode('utf8').encode(CHARSET)
    payload['typeid']  = "4002"
    resp = sess.post(host + form['action'], data=payload)
    if src['subject'].decode('utf8').encode(CHARSET) not in resp.content:
        logger.error('Post Error')
        return ('', str(logger))
    logger.info('Post OK')
    url = resp.url
    # url = 'http://bbs.sciencenet.cn/forum.php?mod=viewthread&tid=' + re.findall("'tid':'(\d+)'", resp.content)[0] + '&extra='
    return (url, str(logger))
