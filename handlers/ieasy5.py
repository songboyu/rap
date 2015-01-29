# -*- coding: utf-8 -*- 
"""凯迪回复模块

@author: HSS
@since: 2014-11-30
@summary: 加拿大加易中文网

"""
import requests, re, random, logging
from bs4 import BeautifulSoup

import config
from utils import *


def login_ieasy5(sess, src):
    """ 加易登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    host = 'http://ieasy5.com/bbs/'
    resp = sess.get('http://ieasy5.com/bbs/thread.php?fid=3')
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'name': 'login_FORM'})

    payload = get_datadic(form, 'gbk')
    payload['pwuser'] = src['username'].decode('utf8').encode('gbk')
    payload['pwpwd'] = src['password'].decode('utf8').encode('gbk')
    # 发送登录post包
    resp = sess.post(host+form['action'], data=payload)
    # 若指定字样出现在response中，表示登录成功
    if u'您已经顺利登录' not in resp.content.decode('gbk'):
        return False
    return True


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
    logger.info('Reply OK')
    return (True, str(logger))


# Coding: gbk
# Captcha: not required
# Login: required
def reply_ieasy5_forum(post_url, src):
    logger = RAPLogger(post_url)
    host = 'http://ieasy5.com/bbs/'
    sess = RAPSession(src)

    if not login_ieasy5(sess, src):
        logger.error('Login Error')
        return (False, str(logger))
    logger.info('Login OK')

    # Step 2: Load post page
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id': 'anchor'})

    # Step 3: Submit
    payload = get_datadic(form, 'gbk')
    if 'subject' in src:
        payload['atc_title'] = src['subject'].decode('utf8').encode('gbk')
    payload['atc_content'] = src['content'].decode('utf8').encode('gbk')

    resp = sess.post(host + form['action'], data=payload)
    soup = BeautifulSoup(resp.content)
    tag = soup.find('div', attrs={'class': 'cc'})
    if u'跳转' not in tag.find('a').text:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))


def post_ieasy5_forum(post_url, src):
    """加拿大加易论坛发主贴模块

    @author: HSS
    @since: 2015-1-24

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   板块地址 http://ieasy5.com/bbs/thread.php?fid=3
    @type post_url:    str

    @param src:        用户名，密码，标题，帖子内容等等。
    @type src:         dict

    @return:           是否发帖成功
    @rtype:            bool

    """
    host = 'http://ieasy5.com/bbs/'
    logger = RAPLogger(post_url)
    sess = RAPSession(src)
    # Step 1: 登录
    if not login_ieasy5(sess, src):
        logger.error(' Login Error')
        return ('', str(logger))
    logger.info(' Login OK')

    fid = re.findall(r'fid=(\d*)', post_url)[0]
    resp = sess.get('http://ieasy5.com/bbs/post.php?fid='+fid)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id': 'mainForm'})
    payload = get_datadic(form)
    payload['atc_title'] = src['subject'].decode('utf8').encode('gbk')
    payload['atc_content'] = src['content'].decode('utf8').encode('gbk')
    payload['step'] = '2'
    payload['pid'] = ''
    payload['action'] = 'new'
    payload['fid'] = fid
    payload['tid'] = '0'
    payload['article'] = '0'
    payload['special'] = '0'
    payload['_hexie'] = 'cn0zz'
    payload['atc_hide'] = '0'

    resp = sess.post(host + form['action'], data=payload)
    soup = BeautifulSoup(resp.content)
    tag = soup.find('div', attrs={'class': 'cc'})
    if u'跳转' not in tag.find('a').text:
        logger.error('Post Error')
        return ('', str(logger))
    logger.info('Post OK')
    url = host + tag.find('a')['href']
    print url
    return (url, str(logger))
    
