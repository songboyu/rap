# -*- coding: utf-8 -*- 

import requests, re
from bs4 import BeautifulSoup

import config
from utils import *

# Coding: gb2312
# Captcha: not required
# Login: required
def reply_creaders_news(post_url, src):
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    s = RAPSession(src)

    r = s.get(post_url)
    soup = BeautifulSoup(r.content)
    # If this is news page, then go to comment page.
    if 'comment.php' not in post_url:
    	post_url = soup.find('a', attrs={'id': 'pmoreurl'})['href']
    	r = s.get(post_url)
    	soup = BeautifulSoup(r.content)

    payload = {
    	'news_id': re.findall('news_id=(\d*)', post_url)[0],
    	'r_nid': re.findall('r_nid=(\d*)', post_url)[0],
    	'username': src['username'],
    	'password': src['password'],
    	'replyid': 0,
    	# The charset of this page is `gb2312` absolutely, but it seems that
    	# `saytext` receives `utf8` only.
    	'saytext': src['content'],
    }
    r = s.post(host + '/headline/postcomment.php', data=payload)
    if u'评论成功'.encode('gb2312') not in r.content:
    	logger.error('Reply Error')
    	return (False, str(logger))
    logger.debug('Reply OK')
    return (True, str(logger))

