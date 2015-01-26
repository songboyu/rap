# -*- coding: utf-8 -*- 

import requests, re, random, logging
from bs4 import BeautifulSoup
from hashlib import md5

import config
from utils import *


def login_aboluowang(sess, src):
    host = 'http://bbs.aboluowang.com/'
    resp = sess.get(host)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id': 'lsform'})
    payload = get_datadic(form)
    payload['username'] = src['username']
    payload['password'] = md5(src['password']).hexdigest()

    resp = sess.post(host + form['action'], data=payload)
    soup = BeautifulSoup(resp.content)
    tag = soup.find('div', attrs={'id': 'messagetext'})
    if tag:
        return False
    return True


# Coding: utf8
# Captcha: arithmetic
# Login: required
def reply_aboluowang_forum(post_url, src):
    if src['TTL'] == 0:
        raise RAPMaxTryException('captcha')
    logger = RAPLogger(post_url)

    host = get_host(post_url)
    sess = RAPSession(src)

    # Step 1: Login
    if not login_aboluowang(sess, src):
        logger.error('Login Error')
        return (False, str(logger))
    logger.info('Login OK')

    # Step 2: Load post page
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'fastpostform'})

    # Step 3: Retrieve captcha question and crack
    resp = sess.get(host + 'misc.php',
                    params={
                        'mod': 'secqaa',
                        'action': 'update',
                        'idhash': hidden_value(form, 'sechash'),
                        'inajax': 1,
                        'ajaxtarget': 'secqaa_' + hidden_value(form, 'sechash'),
                    },
                    headers={'Referer': post_url})

    # Crack the silly captcha question
    # Server responses are as follows: 
    # <root><![CDATA[输入下面问题的答案<br />七加五是多少？]]></root>
    # <root><![CDATA[输入下面问题的答案<br />七加三是多少？]]></root>
    # ...
    chinese_numbers = [u'零', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九']
    formula = resp.content.decode('utf8')
    plus_index = formula.find(u'加')
    a = chinese_numbers.index(formula[plus_index - 1]) 
    b = chinese_numbers.index(formula[plus_index + 1]) 
    seccode = a + b
    logger.info('%d + %d = %d' % (a, b, seccode))

    # Verify the captcha question ACTIVELY.
    resp = sess.get('http://bbs.aboluowang.com/misc.php',
                    params={
                        'mod': 'secqaa',
                        'action': 'check',
                        'idhash': hidden_value(form, 'sechash'),
                        'inajax': 1,
                        'secverify': seccode,
                    },
                    headers={'Referer': post_url})

    # Step 4: Submit and check
    payload = get_datadic(form)
    if 'subject' in src:
        payload['subject'] = src['subject']
    payload['message'] = src['content']
    payload['secanswer'] = seccode

    resp = sess.post(host + form['action'], data=payload)
    soup = BeautifulSoup(resp.content)
    tag = soup.find('div', attrs={'id': 'messagetext'})
    if tag:
        logger.error('Reply Error: ' + tag.find('p').text)
        # Captcha cracking is absolutely right, unless the schema has changed
        # It's not necessary to retry for captcha error
        # But it is necessary now...
        if u'验证问答' in tag.find('p').text:
            src['TTL'] -= 1
            return reply_aboluowang_forum(post_url, src)
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))


# Coding: utf8
# Captcha: required
# Login: not required
def reply_aboluowang_news(post_url, src):
    if src['TTL'] == 0:
        raise RAPMaxTryException('captcha')
    logger = RAPLogger(post_url)

    host = get_host(post_url)
    sess = RAPSession(src)

    # If this is news page, then go to comment page.
    if 'pinlun' not in post_url:
        resp = sess.get(post_url)
        post_url = host + re.findall('(/pinlun[^"]*)', resp.content)[0]

    # Load comment page.
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form')

    # Crack captcha.
    resp = sess.get(host + '/api.php?op=checkcode&code_len=4&font_size=20&width=130&height=50&font_color=&background=&0.23309023911133409',
        headers={
            'Accept': config.accept_image,
            'Referer': post_url,
        })
    seccode = crack_captcha(resp.content)

    # Reply
    payload = get_datadic(form)
    payload['content'] = src['content']
    payload['code'] = seccode
    resp = sess.post(form['action'], data=payload)
    if '操作成功' not in resp.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))


def post_aboluowang_forum(post_url, src):
    if src['TTL'] == 0:
        raise RAPMaxTryException('captcha')
    logger = RAPLogger(post_url)

    host = get_host(post_url)
    sess = RAPSession(src)

    # Step 1: Login
    if not login_aboluowang(sess, src):
        logger.error('Login Error')
        return ('', str(logger))
    logger.info('Login OK')

    # Step 2: Load post page
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'fastpostform'})

    # Step 3: Retrieve captcha question and crack
    resp = sess.get(host + 'misc.php',
                    params={
                        'mod': 'secqaa',
                        'action': 'update',
                        'idhash': hidden_value(form, 'sechash'),
                        'inajax': 1,
                        'ajaxtarget': 'secqaa_' + hidden_value(form, 'sechash'),
                    },
                    headers={'Referer': post_url})

    # Crack the silly captcha question
    # Server responses are as follows: 
    # <root><![CDATA[输入下面问题的答案<br />七加五是多少？]]></root>
    # <root><![CDATA[输入下面问题的答案<br />七加三是多少？]]></root>
    # ...
    chinese_numbers = [u'零', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九']
    formula = resp.content.decode('utf8')
    plus_index = formula.find(u'加')
    a = chinese_numbers.index(formula[plus_index - 1]) 
    b = chinese_numbers.index(formula[plus_index + 1]) 
    seccode = a + b
    logger.info('%d + %d = %d' % (a, b, seccode))

    # Verify the captcha question ACTIVELY.
    resp = sess.get('http://bbs.aboluowang.com/misc.php',
                    params={
                        'mod': 'secqaa',
                        'action': 'check',
                        'idhash': hidden_value(form, 'sechash'),
                        'inajax': 1,
                        'secverify': seccode,
                    },
                    headers={'Referer': post_url})

    # Step 4: Submit and check
    payload = get_datadic(form)
    payload['subject'] = src['subject']
    payload['message'] = src['content']
    payload['secanswer'] = seccode

    resp = sess.post(host + form['action'], data=payload)
    soup = BeautifulSoup(resp.content)
    tag = soup.find('div', attrs={'id': 'messagetext'})
    if tag:
        logger.error('Post Error: ' + tag.find('p').text)
        # Captcha cracking is absolutely right, unless the schema has changed
        # It's not necessary to retry for captcha error
        # But it is necessary now...
        if u'验证问答' in tag.find('p').text:
            src['TTL'] -= 1
            return post_aboluowang_forum(post_url, src)
        return ('', str(logger))
    logger.info('Post OK')
    return (resp.url, str(logger))
