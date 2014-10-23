# -*- coding: utf-8 -*- 

import requests, re, random, logging
from bs4 import BeautifulSoup

import config
from utils import *

# Coding: gb2312
# Captcha: not required
# Login: required
def reply_eulam_forum(post_url, src):
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    s = RAPSession(src)

    payload = {'UserName': src['username'], 'UserPWD': src['password']}
    r = s.post(host + 'login.asp', data=payload)
    if u'操作成功'.encode('gb2312') not in r.content:
        logger.error('Login Error')
        return (False, str(logger))
    logger.debug('Login OK')

    r = s.get(post_url)
    soup = BeautifulSoup(r.content)
    form = soup.find('form', attrs={'name': 'form'})
    payload = get_datadic(form, 'gb2312')
    payload['Body'] = src['content'].decode('utf8').encode('gb2312')
    payload['BBSXPCodeForm'] = ''
    r = s.post(host + 'ReTopic.asp', data=payload)
    if u'操作成功'.encode('gb2312') not in r.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.debug('Reply OK')
    return (True, str(logger))
