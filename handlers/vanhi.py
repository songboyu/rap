# -*- coding: utf-8 -*- 
"""温哥华巅峰

@author: sniper
@since: 2015-1-16
@summary: 温哥华巅峰
"""

import re

from bs4 import BeautifulSoup

from utils import *


def login_vanhi(sess, src):
    # Load login page.
    host = 'http://forum.vanhi.com/'
    resp = sess.get(host + 'member.php?mod=logging&action=login&referer=&infloat=yes&handlekey=login&inajax=1&ajaxtarget=fwin_content_login')
    soup = BeautifulSoup(resp.content)

    form = soup.find('form', attrs={'name': 'login'})
    payload = get_datadic(form, 'gbk')
    payload['username'] = src['username']
    payload['password'] = src['password']

    resp = sess.post(host + form['action'] + '&inajax=1', data=payload)
    if u'欢迎'.encode('gbk') not in resp.content:
        return False
    return True


def reply_vanhi_forum(post_url, src):
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    sess = RAPSession(src)

    # Login
    if not login_vanhi(sess, src):
        logger.error('Login Error')
        return (False, str(logger))
    logger.info('Login OK')

    # Reply
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'fastpostform'})
    payload = get_datadic(form, 'gbk')
    payload['message'] = src['content'].decode('utf8').encode('gbk')

    resp = sess.post(host + form['action'] + '&inajax=1', data=payload)
    if u'成功'.encode('gbk') not in resp.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))


def post_vanhi_forum(post_url, src):
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    sess = RAPSession(src)

    # Login
    if not login_vanhi(sess, src):
        logger.error('Login Error')
        return ('', str(logger))
    logger.info('Login OK')

    # Post
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'fastpostform'})
    payload = get_datadic(form, 'gbk')
    payload['subject'] = src['subject'].decode('utf8').encode('gbk')
    payload['message'] = src['content'].decode('utf8').encode('gbk')

    resp = sess.post(host + form['action'] + '&inajax=1', data=payload)
    if u'主题已发布'.encode('gbk') not in resp.content:
        logger.error('Post Error')
        return ('', str(logger))
    logger.info('Post OK')
    url = 'http://forum.vanhi.com/forum.php?mod=viewthread&tid=' + re.findall("'tid':'(\d+)'", resp.content)[0]
    return (url, str(logger))
