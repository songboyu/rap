# -*- coding: utf-8 -*- 

import requests, re, random, logging
from bs4 import BeautifulSoup
import time

import config
import utils

# Coding: gb2312
# Captcha: not required
# Login: required

CHARSET = 'gb2312'

def login_eulam_forum(s, src):
    """ 欧朗登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    payload = {'UserName': src['username'], 'UserPWD': src['password']}
    r = s.post('http://bbs.eulam.com/login.asp', data=payload)
    if u'操作成功'.encode(CHARSET) not in r.content:
        return False
    return True

def reply_eulam_forum(post_url, src):
    logger = utils.RAPLogger(post_url)
    host = utils.get_host(post_url)
    s = utils.RAPSession(src)

    # Step 1: 登录
    if not login_eulam_forum(s, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.info(' Login OK')

    r = s.get(post_url)
    soup = BeautifulSoup(r.content)
    form = soup.find('form', attrs={'name': 'form'})
    payload = utils.get_datadic(form, CHARSET)
    payload['Body'] = src['content'].decode('utf8').encode(CHARSET)
    payload['BBSXPCodeForm'] = ''
    r = s.post(host + 'ReTopic.asp', data=payload, headers={'Referer': post_url})
    if u'操作成功'.encode(CHARSET) not in r.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))

def get_account_info_eulam_forum(src):
    """ 欧浪账户信息获取函数

    @param src:        用户名，密码
    @type src:         dict

    @return:           账户信息
    @rtype:            dict
    """
    logger = utils.RAPLogger(src['username'])
    sess = utils.RAPSession(src)

    # Step 1: 登录
    if not login_eulam_forum(sess, src):
        logger.error(' Login Error')
        return ({}, str(logger))
    logger.info(' Login OK')

    resp = sess.get('http://bbs.eulam.com/user/Profile.asp?UserName='+src['username'])

    head_image = 'http://bbs.eulam.com/css/css1/images/photobg.gif'

    html = resp.content.decode(CHARSET,'ignore').encode('utf8')

    account_score = re.findall(r'<li>用户魅力：(\d+)</li>', html)[0]
    account_class = re.findall(r'<li>用户角色：(.*?)</li>', html)[0]

    time_register = re.findall(r'<li>注册时间：(.*?)</li>', html)[0]
    year = time.strftime('%Y',time.localtime(time.time()))
    time_last_login = year +'-'+ re.findall(r'<li>上次登录：(.*?)</li>', html)[0]

    login_count = re.findall(r'<li>登录次数：(\d+)</li>', html)[0]

    count_post = re.findall(r'<li>发表原贴：(\d+)</li>', html)[0]
    count_reply = re.findall(r'<li>发表回贴：(\d+)</li>', html)[0]

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
