# -*- coding: utf-8 -*- 

import requests, re, random, logging
from bs4 import BeautifulSoup

import config
from utils import *

# Coding: gb2312
# Captcha: not required
# Login: required
def reply_boxun_forum(post_url, src):
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    s = RAPSession(src)

    r = s.get(post_url)
    soup = BeautifulSoup(r.content)
    form = soup.find('form', attrs={'method': 'POST'})
    payload = get_datadic(form, 'gb2312')
    payload['name'] = src['username']
    payload['usrpwd'] = src['password']
    payload['subject'] = src['subject'].decode('utf8').encode('gb2312')
    payload['body'] = src['content'].decode('utf8').encode('gb2312')
    r = s.post(host + form['action'], data=payload)
    with open('0.html', 'w') as f:
        f.write(r.content)
    if u'错误'.encode('gb2312') in r.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))