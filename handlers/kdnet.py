__author__ = 'boyu'
# -*- coding: utf-8 -*-

import requests, re
from bs4 import BeautifulSoup

import config
from utils import *

# Coding: gb2312
# Captcha: not required
# Login: not required
def reply_kdnet(post_url, src):
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    s = RAPSession(src)
    r = s.get(post_url)

    iframeSrc = re.findall('<iframe src=\"(.*?)\"', r.content)[0]

    r = s.get(iframeSrc.decode('gb2312'))

    soup = BeautifulSoup(r.content)

    form = soup.find('form', attrs={'id': 't_form'})

    payload = get_datadic(form)

    payload['UserName'] = src['username']
    payload['password'] = src['password']
    payload['body'] = src['content'].decode('utf8').encode('gb2312')
    boardid = re.findall('boardid=(.*\d)',post_url)[0]
    r = s.post('http://upfile1.kdnet.net/do_lu_shuiyin.asp?action=sre&method=fastreply&BoardID='+boardid, data=payload)

    print re.findall('=4>(.*?)</font', r.content.decode('gb2312'))[0],


    if u'成功回复'.encode('gb2312') not in r.content:
        logger.error(' Reply Error')
        return (False, str(logger))

    logger.debug(' Reply OK')
    return (True, str(logger))

