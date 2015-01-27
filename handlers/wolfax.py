# -*- coding: utf-8 -*- 

import requests, re, random, logging
from bs4 import BeautifulSoup
from hashlib import md5

import config
from utils import *


def login_wolfax(sess, src):
    host = 'http://bbs.wolfax.com/'
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
def reply_wolfax_forum(post_url, src):
    if src['TTL'] == 0:
        raise RAPMaxTryException('captcha')
    logger = RAPLogger(post_url)

    host = get_host(post_url)
    sess = RAPSession(src)

    if not login_wolfax(sess, src):
        logger.error('Login Error')
        return (False, str(logger))
    logger.info('Login OK')

    # Step 2: Load post page
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'fastpostform'})
    idhash = re.findall('secqaa_(\w*)', str(form))[0]

    # Step 3: Retrieve captcha question and crack
    resp = sess.get(host + 'misc.php',
        params={
            'mod': 'secqaa',
            'action': 'update',
            'idhash': idhash,
        },
        headers={'Referer': post_url})

    # Crack the silly captcha question
    # Server responses are as follows: 
    # '77 + 5 = ?'
    # '26 - 5 = ?'
    # ...
    a, op, b = re.findall("'(\d+) (.) (\d+)", resp.content)[0]
    seccode = int(a) + int(b) if op == '+' else int(a) - int(b)
    logger.info('%s %s %s = %d' % (a, op, b, seccode))

    # Step 4: Submit and check
    payload = get_datadic(form)
    if 'subject' in src:
        payload['subject'] = src['subject']
    payload['secqaahash'] = idhash
    payload['secanswer'] = seccode
    payload['message'] = src['content']

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
            return reply_wolfax_forum(post_url, src)
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))


def post_wolfax_forum(post_url, src):
    if src['TTL'] == 0:
        raise RAPMaxTryException('captcha')
    logger = RAPLogger(post_url)

    host = get_host(post_url)
    sess = RAPSession(src)

    if not login_wolfax(sess, src):
        logger.error('Login Error')
        return ('', str(logger))
    logger.info('Login OK')

    # Step 2: Load post page
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'fastpostform'})
    idhash = re.findall('secqaa_(\w*)', str(form))[0]

    # Step 3: Retrieve captcha question and crack
    resp = sess.get(host + 'misc.php',
        params={
            'mod': 'secqaa',
            'action': 'update',
            'idhash': idhash,
        },
        headers={'Referer': post_url})

    # Crack the silly captcha question
    # Server responses are as follows: 
    # '77 + 5 = ?'
    # '26 - 5 = ?'
    # ...
    a, op, b = re.findall("'(\d+) (.) (\d+)", resp.content)[0]
    seccode = int(a) + int(b) if op == '+' else int(a) - int(b)
    logger.info('%s %s %s = %d' % (a, op, b, seccode))

    # Step 4: Submit and check
    payload = get_datadic(form)
    payload['subject'] = src['subject']
    payload['secqaahash'] = idhash
    payload['secanswer'] = seccode
    payload['message'] = src['content']

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
            return post_wolfax_forum(post_url, src)
        return ('', str(logger))
    logger.info('Post OK')
    return (resp.url, str(logger))


def reply_wolfax_blog(post_url, src):
    if src['TTL'] == 0:
        raise RAPMaxTryException('captcha')
    logger = RAPLogger(post_url)

    host = get_host(post_url)
    sess = RAPSession(src)

    if not login_wolfax(sess, src):
        logger.error('Login Error')
        return (False, str(logger))
    logger.info('Login OK')

    # Step 2: Load post page
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    uid = re.findall('&id=(\d+)', post_url)[0]
    form = soup.find('form', attrs={'id': 'quickcommentform_' + uid})
    idhash = re.findall('secqaa_(\w*)', str(form))[0]

    # Step 3: Retrieve captcha question and crack
    resp = sess.get(host + 'misc.php',
        params={
            'mod': 'secqaa',
            'action': 'update',
            'idhash': idhash,
        },
        headers={'Referer': post_url})

    # Crack the silly captcha question
    # Server responses are as follows: 
    # '77 + 5 = ?'
    # '26 - 5 = ?'
    # ...
    a, op, b = re.findall("'(\d+) (.) (\d+)", resp.content)[0]
    seccode = int(a) + int(b) if op == '+' else int(a) - int(b)
    logger.info('%s %s %s = %d' % (a, op, b, seccode))

    # Step 4: Submit and check
    payload = get_datadic(form)
    if 'subject' in src:
        payload['subject'] = src['subject']
    payload['secqaahash'] = idhash
    payload['secanswer'] = seccode
    payload['message'] = src['content']

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
            return reply_wolfax_forum(post_url, src)
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))


def post_wolfax_blog(post_url, src):
    if src['TTL'] == 0:
        raise RAPMaxTryException('captcha')
    logger = RAPLogger(post_url)

    host = 'http://home.wolfax.com/'
    sess = RAPSession(src)

    if not login_wolfax(sess, src):
        logger.error('Login Error')
        return (False, str(logger))
    logger.info('Login OK')

    resp = sess.get(host + 'home.php?mod=spacecp&ac=blog')
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id': 'ttHtmlEditor'})
    print form
    idhash = re.findall('secqaa_(\w*)', str(form))[0]

    # Step 3: Retrieve captcha question and crack
    resp = sess.get(host + 'misc.php',
        params={
            'mod': 'secqaa',
            'action': 'update',
            'idhash': idhash,
        },
        headers={'Referer': post_url})

    # Crack the silly captcha question
    # Server responses are as follows: 
    # '77 + 5 = ?'
    # '26 - 5 = ?'
    # ...
    a, op, b = re.findall("'(\d+) (.) (\d+)", resp.content)[0]
    seccode = int(a) + int(b) if op == '+' else int(a) - int(b)
    logger.info('%s %s %s = %d' % (a, op, b, seccode))

    # Step 4: Submit and check
    payload = get_datadic(form)
    if 'subject' in src:
        payload['subject'] = src['subject']
    payload['secqaahash'] = idhash
    payload['secanswer'] = seccode
    payload['message'] = src['content']

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
            return reply_wolfax_forum(post_url, src)
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))
    