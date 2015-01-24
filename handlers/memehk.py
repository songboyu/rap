# -*- coding: utf-8 -*- 

import requests, re, random, logging
from bs4 import BeautifulSoup

import config
from utils import *


def login_memehk(sess, src):
    host = 'http://forum.memehk.com/'
    resp = sess.get(host + 'forum.php')
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id': 'lsform'})
    payload = get_datadic(form)
    payload['username'] = src['username']
    payload['password'] = src['password']
    payload['fastloginfield'] = 'username'

    resp = sess.post(host + form['action'] + '&inajax=1', data=payload)
    if '失敗' in resp.content:
        return False
    return True


# Coding: utf8
# Captcha: not required
# Login: required
def reply_memehk_forum(post_url, src):
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    sess = RAPSession(src)

    if not login_memehk(sess, src):
        logger.error('Login Error')
        return (False, str(logger))
    logger.info('Login OK')

    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id': 'fastpostform'})
    payload = get_datadic(form)
    payload['message'] = src['content']
    resp = sess.post(host + form['action'] + '&inajax=1', data=payload)
    if 'errorhandle_fastpost' in resp.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))
