# -*- coding: utf-8 -*- 

import requests, re, random, logging
from bs4 import BeautifulSoup

import config
from utils import *


def login_memehk(sess, src):
    host = 'http://forum.memehk.com/'
    resp = sess.get(host + 'forum.php')
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id': 'lsform'})
    payload = get_datadic(form)
    payload['username'] = src['username']
    payload['password'] = src['password']
    payload['fastloginfield'] = 'username'

    resp = sess.post(host + form['action'] + '&inajax=1', data=payload)
    if '失敗' in resp.content:
        return False
    return True


# Coding: utf8
# Captcha: not required
# Login: required
def reply_memehk_forum(post_url, src):
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    sess = RAPSession(src)

    if not login_memehk(sess, src):
        logger.error('Login Error')
        return (False, str(logger))
    logger.info('Login OK')

    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id': 'fastpostform'})
    payload = get_datadic(form)
    payload['message'] = src['content']
    resp = sess.post(host + form['action'] + '&inajax=1', data=payload)
    if 'errorhandle_fastpost' in resp.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))


def post_memehk_forum(post_url, src):
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    sess = RAPSession(src)

    if not login_memehk(sess, src):
        logger.error('Login Error')
        return ('', str(logger))
    logger.info('Login OK')

    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id': 'fastpostform'})
    payload = get_datadic(form)
    payload['subject'] = src['subject']
    payload['message'] = src['content']

    resp = sess.post(host + form['action'] + '&inajax=1', data=payload)
    if '主題已發佈' not in resp.content:
        logger.error('Post Error')
        return ('', str(logger))
    logger.info('Post OK')
    url = 'http://forum.memehk.com/forum.php?mod=viewthread&tid=' + re.findall("'tid':'(\d+)'", resp.content)[0]
    return (url, str(logger))


def get_account_info_memehk_forum(src):
    """ 迷米香港账户信息获取函数

    @param src:        用户名，密码
    @type src:         dict

    @return:           账户信息
    @rtype:            dict
    """
    logger = RAPLogger(src['username'])
    sess = RAPSession(src)

    # Step 1: 登录
    if not login_memehk(sess, src):
        logger.error(' Login Error')
        return ({}, str(logger))
    logger.info(' Login OK')

    resp = sess.get('http://forum.memehk.com/home.php?mod=space')

    head_image = re.findall(r'img src="(.*avatar.*)"', resp.content)[0]

    account_score = re.findall(r'<li><em>積分</em>(.*?)</li>', resp.content)[0]
    account_class = re.findall(r'ac=usergroup.*>(.*?)</a>', resp.content)[0]

    time_register = re.findall(r'<li><em>註冊時間</em>(.*?)</li>', resp.content)[0]
    time_last_login = re.findall(r'<li><em>上次活動時間</em>(.*?)</li>', resp.content)[0]

    login_count = ''

    count_post = re.findall(r'主題數 (.*?)<', resp.content)[0]
    count_reply = re.findall(r'回帖數 (.*?)<', resp.content)[0]

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
