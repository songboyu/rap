# -*- coding: utf-8 -*- 

import requests, re, random, logging
from bs4 import BeautifulSoup

import config
from utils import *

# Coding: utf8
# Captcha: required
# Login: not required
def reply_secretchina_news(post_url, src):
    if src['TTL'] == 0:
        raise RAPMaxTryException('captcha')

    post_url = post_url.replace('m.secretchina', 'www.secretchina')
    logger = RAPLogger(post_url)

    host = get_host(post_url)
    s = RAPSession(src)

    # Step 1: Load post page
    r = s.get(post_url)
    soup = BeautifulSoup(r.content)
    form = soup.find('form', attrs={'id': 'comment-form'})
    assert form, 'HTML has changed!'

    # Step 2: Crack captcha
    r = s.get(host + '/captcha?_=' + str(random.random()))
    captcha_url = 'http://www.secretchina.com/cache/' + re.findall('(\w*\.png)', r.content)[0]
    r = s.get(captcha_url, 
        headers={
            'Accept': config.accept_image,
            'Referer': post_url,
        })
    seccode = crack_captcha(r.content)

    # Step 3: Submit and check
    payload = get_datadic(form)
    if 'nickname' in src:
        payload['nickname'] = src['nickname']
    payload['comment'] = src['content']
    payload['captcha'] = seccode

    r = s.post(host + form['action'], data=payload)
    if 'success' not in r.content: 
        logger.error('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))