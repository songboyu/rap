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


def reply_m_secretchina_news(post_url, src):
    if src['TTL'] == 0:
        raise RAPMaxTryException('captcha')

    logger = RAPLogger(post_url)

    host = get_host(post_url)
    s = RAPSession(src)

    # Step 1: Load post page
    r = s.get(post_url)
    soup = BeautifulSoup(r.content)
    form = soup.find('form', attrs={'id': 'comment-form'})
    assert form, 'HTML has changed!'

    # Step 2: Crack the silly captcha question
    # Server responses are as follows:
    # '77 加 5 = ?'
    # '26 加 5 = ?'
    r = s.get('http://m.secretchina.com/ajax_comments/js_reload_captcha/comment_form')
    soup = BeautifulSoup(r.content)
    captcha_sid = soup.select('input#edit-captcha-sid')[0]['value']
    captcha_token = soup.select('input#edit-captcha-token')[0]['value']

    span = soup.select('span.field-prefix')[0].text
    a, op, b = re.findall(r'(\d+) (.) (\d+)', span)[0]

    captcha_response = int(a) + int(b) if op == u'加' else int(a) - int(b)
    logger.info('%s %s %s = %d' % (a, op, b, captcha_response))
    # Step 3: Submit and check
    payload = get_datadic(form)
    if 'nickname' in src:
        payload['name'] = src['nickname']
    else:
        payload['name'] = '看中国网友'

    payload['comment'] = src['content']
    payload['captcha_sid'] = captcha_sid
    payload['captcha_token'] = captcha_token
    payload['captcha_response'] = captcha_response

    r = s.post(host + '/ajax_comments/js', data=payload)
    if 'comment-text' not in r.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))