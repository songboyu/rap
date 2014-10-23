# -*- coding: utf-8 -*- 

import requests, re, random, logging
from bs4 import BeautifulSoup

import config
from utils import *

# Coding: gb2312
# Captcha: required
# Login: not required
def reply_ieasy5_news(post_url, src):
    if src['TTL'] == 0:
        raise RAPMaxTryException('captcha')
    logger = RAPLogger(post_url)

    host = get_host(post_url)
    s = RAPSession(src)

    # Step 1: Load post page
    r = s.get(post_url)
    soup = BeautifulSoup(r.content)
    form_url = host + soup.find('iframe', attrs={'id': 'o'})['src']

    # Step 2: Get real form html
    r = s.get(form_url)
    soup = BeautifulSoup(r.content)

    # Step 3: Retrieve captcha and crack
    r = s.get(host + 'e/ShowKey?v=pl' + str(random.random()),
        headers={
            'Accept': config.accept_image,
            'Referer': post_url,
        })
    seccode = crack_captcha(r.content)

    # Step 4: Submit and check
    form = soup.find('form', attrs={'name': 'saypl'})
    payload = get_datadic(form, 'gb2312')
    if 'nickname' in src:
        payload['username'] = src['nickname'].decode('utf8').encode('gb2312')
    payload['saytext'] = src['content'].decode('utf8').encode('gb2312')
    payload['key'] = seccode

    r = s.post(host + 'e/enews/index.php', data=payload)
    soup = BeautifulSoup(r.content)
    tag = soup.find('span', attrs={'class': 'rred'})
    if u'评论成功' not in tag.text:
        logger.error('Reply Error: ' + tag.text)
        if u'验证码' in tag.text:
            # Captcha error, retry
            src['TTL'] -= 1
            return reply_ieasy5_news(post_url, src)
        return (False, str(logger))
    logger.debug('Reply OK')
    return (True, str(logger))

# Coding: gbk
# Captcha: not required
# Login: required
def reply_ieasy5_forum(post_url, src):
    logger = RAPLogger(post_url)
    host = 'http://ieasy5.com/bbs/'
    s = RAPSession(src)

    # Step 1: Login
    r = s.get(host)
    soup = BeautifulSoup(r.content)
    form = soup.find('form', attrs={'name': 'login_FORM'})
    payload = {
        'jumpurl': host + 'index.php',
        'step': 2,
        'pwuser': src['username'],
        'pwpwd': src['password'],
        'lgt': 0,
    }

    r = s.post(host + form['action'], data=payload)
    soup = BeautifulSoup(r.content)
    tag = soup.find('span')
    if u'顺利登录' not in tag.text:
        logger.error('Login Error: ' + tag.text)
        return (False, str(logger))
    logger.debug('Login OK')

    # Step 2: Load post page
    r = s.get(post_url)
    soup = BeautifulSoup(r.content)
    form = soup.find('form', attrs={'id': 'anchor'})

    # Step 3: Submit
    payload = get_datadic(form, 'gbk')
    if 'subject' in src:
        payload['atc_title'] = src['subject'].decode('utf8').encode('gbk')
    payload['atc_content'] = src['content'].decode('utf8').encode('gbk')

    r = s.post(host + form['action'], data=payload)
    soup = BeautifulSoup(r.content)
    tag = soup.find('div', attrs={'class': 'cc'})
    if u'跳转' not in tag.find('a').text:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.debug('Reply OK')
    return (True, str(logger))