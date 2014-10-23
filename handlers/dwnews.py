# -*- coding: utf-8 -*- 

import requests, re, random
from bs4 import BeautifulSoup

import config
from utils import *

# Coding: utf8
# Captcha: not required
# Login: not required
def reply_dwnews_news(post_url, src):
    s = RAPSession(src)
    logger = RAPLogger(post_url)

    r = s.get(post_url)
    ikey = re.findall('ikey = "(\w*)"', r.content)[0]

    r = s.get('http://blog.dwnews.com/index.php', params={
            'r': 'comment/post',
            'callback': 'success_jsonpCallback',
            'doitem': 'post',
            'content': src['content'],
            'type': 'news',
            'author': 9999999,
            'url': ikey,
            'club_id': '',
            'facebook': 0,
            'twitter': 0,
            '_': str(random.random()),
        })

    if 'success' not in r.content:
        logger.debug('Reply Error')
        return (False, str(logger))
    logger.debug('Reply OK')
    return (True, str(logger))

# Coding: utf8
# Captcha: not required
# Login: not required
def reply_dwnews_blog(post_url, src):
    s = RAPSession(src)
    logger = RAPLogger(post_url)

    r = s.get(post_url)
    ikey = re.findall('ikey = "(\w*)"', r.content)[0]
    club_id = re.findall('post-(\d*)', post_url)[0]

    r = s.get('http://blog.dwnews.com/index.php', params={
            'r': 'comment/post',
            'callback': 'success_jsonpCallback',
            'doitem': 'post',
            'content': src['content'],
            'type': 'club',
            'author': 9999999,
            'url': ikey,
            'club_id': club_id,
            'facebook': 0,
            'twitter': 0,
        })

    if 'success' not in r.content:
        logger.debug('Reply Error')
        return (False, str(logger))
    logger.debug('Reply OK')
    return (True, str(logger))