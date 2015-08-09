# -*- coding: utf-8 -*-

import re
import random

import requests
from bs4 import BeautifulSoup

from utils import *
import config

def get_userinfo(time_str, username):
    a = sum([int(x) for x in re.split(r'[- :]', time_str)]) % 60
    b = sum([ord(x) for x in username.lower()]) % 60
    return a * b

def login_csdn(sess, src):
    resp = sess.get('http://passport.csdn.net/account/login')
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id': 'fm1'})
    payload = get_datadic(form)
    payload['username'] = src['username']
    payload['password'] = src['password']
    resp = sess.post('http://passport.csdn.net/account/login', data=payload)
    if src['username'] not in resp.content:
        return False
    return True

def post_csdn_blog(post_url, src):
    logger = RAPLogger(post_url)
    sess = RAPSession(src)

    if not login_csdn(sess, src):
        logger.error('Login Error')
        return ('', str(logger))
    logger.info('Login OK')

    resp = sess.get('http://write.blog.csdn.net/postedit')
    userinfo1 = re.findall(r'id="userinfo1" value="(.*?)"', resp.content)[0]
    payload = {
        'titl': src['subject'],
        'typ': 1,
        'cont': src['content'],
        'desc': '',
        'tags': '',
        'flnm': '',
        'chnl': 7,
        'comm': 2,
        'level': 0,
        'tag2': '',
        'artid': 0,
        'checkcode': 'undefined',
        'userinfo1': get_userinfo(userinfo1, sess.s.cookies['UserName']),
        'stat': 'publish',
    }
    resp = sess.post('http://write.blog.csdn.net/postedit?edit=1&isPub=1&joinblogcontest=undefined&r=' + str(random.random()), data=payload)
    # with open('1.html', 'w') as f:
    #     f.write(resp.content)
    if '成功' not in resp.content:
        logger.error('Post Error')
        return ('', str(logger))
    return (resp.json()['data'], str(logger))

def post_csdn_forum(post_url, src):
    logger = RAPLogger(post_url)
    sess = RAPSession(src)

    if not login_csdn(sess, src):
        logger.error('Login Error')
        return ('', str(logger))
    logger.info('Login OK')

    resp = sess.get('http://bbs.csdn.net/topics/new')
    with open('0.html', 'w') as f:
        f.write(resp.content)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'new_topic'})
    payload = get_datadic(form)
    payload['topic[title]'] = src['subject']
    payload['topic[body]'] = src['content']
    payload['topic[forum_id]'] = 'OtherITnews'
    payload['topic[point]'] = '0',

    # Get captcha.
    resp = sess.get('http://bbs.csdn.net/captchas/new')
    captcha_code = re.findall('code=(\w+)', resp.content)[0]
    captcha_time = re.findall('time=(\d+)', resp.content)[0]
    resp = sess.get('http://bbs.csdn.net/simple_captcha?code=%s&time=%s' % (captcha_code, captcha_time), 
                    headers={'Accept': config.accept_image, 
                             'Referer': 'http://bbs.csdn.net/topics/new'})
    # with open('1.jpg', 'wb') as f:
    #     f.write(resp.content)
    seccode = crack_captcha(resp.content)
    logger.info('Captcha ' + seccode)

    payload['captcha'] = seccode
    payload['captcha_key'] = captcha_code
    for k in payload:
        print k, payload[k]
    resp = sess.post('http://bbs.csdn.net/topics', data=payload)
    with open('1.html', 'w') as f:
        f.write(resp.content)

    return ('', str(logger))
