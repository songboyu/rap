# -*- coding: utf-8 -*- 

import requests, re, random, logging
from bs4 import BeautifulSoup

import config
from utils import *

def login_wenxuecity(s, src):
    payload = {
        'redirect': 'http://bbs.wenxuecity.com/',
        'username': src['username'],
        'password': src['password'],
        'login': '登录',
    }
    # Terminate the endless redirection, reload the page instead to check success.
    r = s.post('http://bbs.wenxuecity.com/members/passport.php?act=topbar_post&iframe=0', data=payload, allow_redirects=False)
    r = s.get('http://passport.wenxuecity.com/members/script/members.php')
    if 'login_in_box' not in r.content:
        return False
    return True

# Coding: utf8
# Captcha: not required
# Login: required
def reply_wenxuecity_forum(post_url, src):
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    s = RAPSession(src)

    # Since subject is mandatory, we take first few words as default title.
    if 'subject' not in src:
        src['subject'] = src['content'].decode('utf8')[:15].encode('utf8')

    if not login_wenxuecity(s, src):
        logger.error('Login Error')
        return (False, str(logger))
    logger.debug('Login OK')

    r = s.get(post_url)
    soup = BeautifulSoup(r.content)
    form = soup.find('form', attrs={'id': 'postform'})
    payload = get_datadic(form)
    payload['title'] = src['subject']
    payload['msgbodytext'] = src['content']
    # How to confirm reply OK?
    # Terminate the endless redirection, reload the page instead to check success.
    r = s.post(host + form['action'], data=payload, allow_redirects=False)
    r = s.get(post_url)
    if src['content'] not in r.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.debug('Reply OK')
    return (True, str(logger))

# Coding: utf8
# Captcha: not required
# Login: required
def reply_wenxuecity_news(post_url, src):
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    s = RAPSession(src)

    if not login_wenxuecity(s, src):
        logger.error('Login Error')
        return (False, str(logger))
    logger.debug('Login OK')

    r = s.get(post_url)
    soup = BeautifulSoup(r.content)
    # If this is news page, then go to comment page.
    if 'act=comment' not in post_url:
        post_url = host + soup.find('div', attrs={'class': 'postcomment'}).find('a')['href']
        r = s.get(post_url)
        soup = BeautifulSoup(r.content)

    form = soup.find('form', attrs={'id': 'postform'})
    payload = get_datadic(form)
    payload['msgbody'] = src['content']
    r = s.post(host + 'news' + form['action'].strip('.'), data=payload)
    if src['content'] not in r.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.debug('Reply OK')
    return (True, str(logger))

# Coding: utf8
# Captcha: not required
# Login: required
def reply_wenxuecity_blog(post_url, src):
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    s = RAPSession(src)

    if not login_wenxuecity(s, src):
        logger.error('Login Error')
        return (False, str(logger))
    logger.debug('Login OK')

    r = s.get(post_url)
    soup = BeautifulSoup(r.content)
    form = soup.find('form', attrs={'action': '/blog/index.php?act=commentAdd'})
    payload = get_datadic(form)
    payload['postcomments'] = src['content']
    # Terminate the endless redirection, reload the page instead to check success.
    r = s.post(host + form['action'], data=payload, allow_redirects=False)
    r = s.get(post_url)
    if src['content'] not in r.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.debug('Reply OK')
    return (True, str(logger))
