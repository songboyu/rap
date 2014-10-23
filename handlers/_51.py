# -*- coding: utf-8 -*- 

import requests, re, random, logging
from bs4 import BeautifulSoup

import config
from utils import *

# Coding: utf8
# Captcha: not required
# Login: required
def reply_51_forum(post_url, src):
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    s = RAPSession(src)

    r = s.get(host + 'logging.php?action=login')
    soup = BeautifulSoup(r.content)
    form = soup.find('form', attrs={'name': 'login'})
    payload = get_datadic(form)
    payload['username'] = src['username']
    payload['password'] = src['password']
    payload['fastloginfield'] = 'username'
    r = s.post(host + form['action'] + '&inajax=1', data=payload)
    if '欢迎您回来' not in r.content:
        logger.error('Login Error')
        return (False, str(logger))
    logger.debug('Login OK')

    r = s.get(post_url)
    soup = BeautifulSoup(r.content)
    form = soup.find('form', attrs={'id': 'fastpostform'})
    payload = get_datadic(form)
    payload['message'] = src['content']
    r = s.post(host + form['action'] + '&inajax=1', data=payload)
    if '对不起' in r.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.debug('Reply OK')
    return (True, str(logger))
