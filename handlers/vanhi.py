# -*- coding: utf-8 -*- 

import requests, re, random, logging
from bs4 import BeautifulSoup
from hashlib import md5
import PyV8

import config
from utils import *

# Coding: gbk
# Captcha: required
# Login: required
def reply_vanhi_forum(post_url, src):

    # Some sub functions to streamline the logic
    # Caution: `host`, `s`, `post_url` and `src` will be used in sub functions
    def get_seccodehash(url):
        for i in range(src['TTL']):
            r = s.get(url)
            if len(r.content) < 3000:
                # Handle JS redirection
                soup = BeautifulSoup(r.content)
                js = soup.find('script').text
                context = PyV8.JSContext()
                context.enter()
                context.eval('var window = new Object(), location = new Object();')
                context.eval('var url, get_url = function (x) {url = x};');
                context.eval('location.assign = get_url, location.replace = get_url;')
                context.eval(js)
                real_url = context.eval('url || location.href')
                logger.debug(real_url)
                r = s.get(host + real_url)
            ret = re.findall('seccode_(\w*)', r.content)
            if ret:
                return r, ret[0]
            logger.error('Seccodehash not found')
        raise RAPMaxTryException('get_seccodehash')

    def get_captcha(seccodehash):
        for i in range(src['TTL']):
            r = s.get(host + 'misc.php?mod=seccode&action=update&idhash=%s&%s&modid=member::logging' % (seccodehash, str(random.random())))
            captcha_url = re.findall('run\("(.*?)"', r.content)[0] + '0'
            r = s.get(host + captcha_url, headers={'Accept': config.accept_image, 'Referer': host})
            if len(r.content) > 100:
                # A real captcha image
                seccode = crack_captcha(r.content)
                return seccode
            logger.error('Captcha busy now')
        raise RAPMaxTryException('get_captcha')

    def login_1():
        r, seccodehash = get_seccodehash(host + 'member.php?mod=logging&action=login&referer=&infloat=yes&handlekey=login&inajax=1&ajaxtarget=fwin_content_login')
        html = strip_cdata(r.content)
        soup = BeautifulSoup(html)
        form = soup.find('form', attrs={'name': 'login'})

        for i in range(src['TTL']):
            seccode = get_captcha(seccodehash)
            payload = get_datadic(form, 'gbk')
            payload['username'] = src['username']
            payload['password'] = src['password']
            payload['seccodeverify'] = seccode

            r = s.post(host + form['action'], data=payload)
            ret = re.findall("location\.href='(.*)'", r.content)
            if ret:
                logger.debug('Login 1 OK')
                return host + ret[0]
            logger.error('Login 1 Error')
        raise RAPMaxTryException('login_1')

    def login_2(login_url):
        r, seccodehash = get_seccodehash(login_url)
        html = strip_cdata(r.content)
        soup = BeautifulSoup(html)
        form = soup.find('form', attrs={'name': 'login'})

        for i in range(src['TTL']):
            seccode = get_captcha(seccodehash)
            payload = get_datadic(form, 'gbk')
            payload['seccodehash'] = seccodehash
            payload['seccodeverify'] = seccode

            r = s.post(host + form['action'], data=payload)
            soup = BeautifulSoup(r.content)
            tag = soup.find('div', attrs={'id': 'messagetext'})
            if tag and tag.find('a') and hasattr(tag.find('a'), 'text') and u'自动跳转' in tag.find('a').text:
                logger.debug('Login 2 OK')
                return
            logger.error('Login 2 Error')
        raise RAPMaxTryException('login_2')

    def submit():
        r, seccodehash = get_seccodehash(post_url)
        html = strip_cdata(r.content)
        soup = BeautifulSoup(html)
        form = soup.find('form', attrs={'id':'fastpostform'})

        for i in range(src['TTL']):
            seccode = get_captcha(seccodehash)
            payload = get_datadic(form, 'gbk')
            if 'subject' in src:
                payload['subject'] = src['subject'].decode('utf8').encode('gbk')
            payload['seccodehash'] = seccodehash
            payload['seccodeverify'] = seccode
            payload['message'] = src['content'].decode('utf8').encode('gbk')

            r = s.post(host + form['action'], data=payload)
            soup = BeautifulSoup(r.content)
            tag = soup.find('div', attrs={'id': 'messagetext'})
            if not tag:
                logger.debug('Reply OK')
                return (True, str(logger))
            logger.error(tag.find('p').text)
        raise RAPMaxTryException('submit')

    # Caution: `host` and `s` will be used in sub functions
    host = get_host(post_url)
    s = RAPSession(src)
    logger = RAPLogger(post_url)

    # Login twice
    login_2(login_1())

    # Submit
    return submit()