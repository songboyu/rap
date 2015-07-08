# -*- coding: utf-8 -*- 
import urllib
import time
import StringIO
# from PIL import Image
import binascii

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
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    sess = RAPSession(src)

    if not login_wolfax(sess, src):
        logger.error('Login Error')
        return (False, str(logger))
    logger.info('Login OK')

    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'fastpostform'})
    payload = get_datadic(form)
    payload['message'] = src['content']

    resp = sess.post(host + form['action'], data=payload)
    soup = BeautifulSoup(resp.content)
    tag = soup.find('div', attrs={'id': 'messagetext'})
    if tag:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))


def post_wolfax_forum(post_url, src):
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
    payload = get_datadic(form)
    payload['subject'] = src['subject']
    payload['message'] = src['content']

    resp = sess.post(host + form['action'], data=payload)
    soup = BeautifulSoup(resp.content)
    tag = soup.find('div', attrs={'id': 'messagetext'})
    if tag:
        logger.error('Post Error')
        return ('', str(logger))
    logger.info('Post OK')
    return (resp.url, str(logger))


def reply_wolfax_blog(post_url, src):
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
    payload = get_datadic(form)
    payload['message'] = src['content']

    resp = sess.post(host + form['action'], data=payload)
    soup = BeautifulSoup(resp.content)
    tag = soup.find('div', attrs={'id': 'messagetext'})
    if tag:
        logger.error('Reply Error')
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
    payload = get_datadic(form)
    if 'subject' in src:
        payload['subject'] = src['subject']
    payload['message'] = src['content']
    payload['catid'] = 1

    resp = sess.post(host + form['action'], data=payload)
    soup = BeautifulSoup(resp.content)
    tag = soup.find('div', attrs={'id': 'messagetext'})
    if tag:
        logger.error('Post Error')
        return ('', str(logger))
    logger.info('Post OK')
    return (resp.url, str(logger))


def get_account_info_wolfax_forum(src):
    logger = RAPLogger('wolfax=>' + src['username'])
    sess = RAPSession(src)

    if not login_wolfax(sess, src):
        logger.error('Login Error')
        return ({}, str(logger))
    logger.info('Login OK')

    resp = sess.get('http://bbs.wolfax.com')
    soup = BeautifulSoup(resp.content)
    resp = sess.get('http://bbs.wolfax.com/' + soup.select('strong.vwmy a')[0]['href'] + '&do=profile')

    head_image = re.findall('avtm"><img src="(.*?)"', resp.content)[0]
    account_score = int(re.findall('积分</em>(\d+)', resp.content)[0])
    account_class = re.findall('用户组.*_blank">(.*?)<', resp.content)[0]
    time_register = re.findall('注册时间</em>(.*?)<', resp.content)[0]
    time_last_login = re.findall('最后访问</em>(.*?)<', resp.content)[0]
    # 铜板 代替 登录次数
    login_count = int(re.findall('铜板</em>(\d+)', resp.content)[0])
    count_post = int(re.findall('主题数 (\d+)', resp.content)[0])
    count_reply = int(re.findall('回帖数 (\d+)', resp.content)[0])

    account_info = {
        #########################################
        # 用户名
        'username':src['username'],
        # 密码
        'password':src['password'],
        # 头像图片
        'head_image':head_image,
        #########################################
        # 积分
        'account_score':account_score,
        # 等级
        'account_class':account_class,
        #########################################
        # 注册时间
        'time_register':time_register,
        # 最近登录时间
        'time_last_login':time_last_login,
        # 登录次数
        'login_count':login_count,
        #########################################
        # 主帖数
        'count_post':count_post,
        # 回复数
        'count_reply':count_reply
        #########################################
    }
    logger.info('Get account info OK')
    return (account_info, str(logger))

def upload_head_wolfax_forum(src):
    logger = RAPLogger('Upload head wolfax_forum=>' + src['username'])
    sess = RAPSession(src)

    # Step 1: 登录
    if not login_wolfax(sess, src):
        logger.error('Login Error')
        return ('', str(logger))
    logger.info('Login OK')

    resp = sess.get('http://home.wolfax.com/home.php?mod=spacecp&ac=avatar')
    input = urllib.unquote(re.findall(r'input=(.*?)&',resp.content)[0])
    agent = re.findall(r'agent=(.*?)&',resp.content)[0]
    head_url = re.findall(r'<td><img src="(.*?)"',resp.content)[0]
    print 'input:',input
    print 'agent:',agent

    # payload = {
    #     'Filename': (None, src['head'].split('/')[-1]),
    #     'Filedata': (src['head'].split('/')[-1], open(src['head'], 'rb'), 'application/octet-stream'),
    #     'Upload': (None,'Submit Query')
    # }
    # params = {
    #     'm':'user',
    #     'inajax':'1',
    #     'a':'uploadavatar',
    #     'appid':'1',
    #     'input':input,
    #     'agent':agent,
    #     'avatartype':'virtual'
    # }
    # resp = sess.post('http://uc.wolfax.com/index.php', files=payload, params=params)

    # buff = StringIO.StringIO()
    #
    # img = Image.open(src['head'])
    #
    # img.thumbnail((200,200),Image.ANTIALIAS)
    # img.save(buff, format='jpeg')
    # avatar1 = buff.getvalue()
    # avatar1 = binascii.hexlify(avatar1).upper()
    #
    # img.thumbnail((120,120),Image.ANTIALIAS)
    # img.save(buff, format='jpeg')
    # avatar2 = buff.getvalue()
    # avatar2 = binascii.hexlify(avatar2).upper()
    #
    # img.thumbnail((48,48),Image.ANTIALIAS)
    # img.save(buff, format='jpeg')
    # avatar3 = buff.getvalue()
    # avatar3 = binascii.hexlify(avatar3).upper()
    #
    # buff.close()

    avatar1 = binascii.hexlify(open(src['head'],'rb').read()).upper()
    avatar2 = avatar1
    avatar3 = avatar1

    params = {
        'm':'user',
        'inajax':'1',
        'a':'rectavatar',
        'appid':'1',
        'input':input,
        'agent':agent,
        'avatartype':'virtual'
    }
    payload = {
        'avatar1':avatar1,
        'avatar2':avatar2,
        'avatar3':avatar3,
        'urlReaderTS':str(time.time()*1000)
    }
    resp = sess.post('http://uc.wolfax.com/index.php', data=payload, params=params)


    print resp.content
    if 'success="1"' in resp.content:
        logger.info('uploadavatar OK')
        return (head_url, str(logger))
    else:
        logger.info('uploadavatar Error')
        return ('', str(logger))
