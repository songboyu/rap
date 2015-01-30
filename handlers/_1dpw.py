# -*- coding: utf-8 -*-
"""加国华人网模块

@author: HSS
@since: 2014-10-20
@summary: 加国华人网

@var CHARSET: 加国华人网网页编码
@type CHARSET: str

"""
import re
import time

from bs4 import BeautifulSoup

import utils

def login_1dpw(post_url, sess, src):
    """ 加国华人网登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    # 获得回复form
    form = soup.find('form', attrs={'id': 'lsform'})
    # 构造回复参数
    payload = utils.get_datadic(form)
    payload['username'] = src['username']
    payload['password'] = src['password']
    # 发送登录post包
    resp = sess.post('http://bbs.1dpw.com/' + form['action'], data=payload)
    # 若指定字样出现在response中，表示登录成功
    if src['username'] not in resp.content:
        return False
    return True

def reply_1dpw_forum(post_url, src):
    """ 加国华人网发回复函数（10个字符）

    @param post_url:   帖子地址
    @type post_url:    str

    @param src:        用户名，密码，内容，等等。
    @type src:         dict

    @return:           是否回复成功
    @rtype:            bool

    """
    host = utils.get_host(post_url)
    logger = utils.RAPLogger(post_url)
    sess = utils.RAPSession(src)
    # Step 1: 登录
    if not login_1dpw(post_url, sess, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.info(' Login OK')

    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    # 获得回复form
    form = soup.find('form', attrs={'id': 'fastpostform'})
    # 构造回复参数
    payload = utils.get_datadic(form)
    payload['message'] = src['content']
    payload['posttime'] = int(time.time())
    # 发送登录post包
    resp = sess.post(host + form['action'] + '&inajax=1', data=payload)
    # 若指定字样出现在response中，表示发帖成功
    if 'Database' not in resp.content:
        logger.error(' Reply Error')
        return (False, str(logger))
    logger.info(' Reply OK')
    return (True, str(logger))

def post_1dpw_forum(post_url, src):
    """ 加国华人网发主贴函数

    @param post_url:   板块地址 如：http://bbs.1dpw.com/forum-71-1.html
    @type post_url:    str

    @param src:        用户名，密码，标题，主帖内容，等等。
    @type src:         dict

    @return:           是否发帖成功，帖子URL
    @rtype:            bool,str

    """
    host = utils.get_host(post_url)
    logger = utils.RAPLogger(post_url)
    sess = utils.RAPSession(src)
    # Step 1: 登录
    if not login_1dpw(post_url, sess, src):
        logger.error(' Login Error')
        return ('', str(logger))
    logger.info(' Login OK')

    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    # 获得回复form
    form = soup.find('form', attrs={'id': 'fastpostform'})
    # 构造回复参数
    payload = utils.get_datadic(form)
    payload['subject'] = src['subject']
    payload['message'] = src['content']
    payload['posttime'] = int(time.time())
    # 发送登录post包
    resp = sess.post(host + form['action'] + '&inajax=1', data=payload)
    # 若指定字样出现在response中，表示发帖成功
    if '主题已发布' not in resp.content:
        logger.error(' Post Error')
        return ('', str(logger))
    logger.info(' Post OK')
    url = host + re.findall(r'succeedhandle_fastnewpost\(\'(.*?)\'', resp.content)[0]
    print url
    return (url, str(logger))


def get_account_info_1dpw_forum(src):
    """ 加国华人网账户信息获取函数

    @param src:        用户名，密码
    @type src:         dict

    @return:           账户信息
    @rtype:            dict
    """
    logger = utils.RAPLogger(src['username'])
    sess = utils.RAPSession(src)

    # Step 1: 登录
    if not login_1dpw('http://bbs.1dpw.com/',sess, src):
        logger.error(' Login Error')
        return ({}, str(logger))
    logger.info(' Login OK')

    resp = sess.get('http://bbs.1dpw.com/')
    url = re.findall(r'href="(.*?)".*title="访问我的空间"',resp.content)[0]
    resp = sess.get(url.replace('&amp;','&'))

    head_image = re.findall(r'img src="(.*avatar.*)"', resp.content)[0]

    account_score = re.findall(r'<li><em>积分</em>(.*?)</li>', resp.content)[0]
    account_class = re.findall(r'ac=usergroup.*>(.*?)</a>', resp.content)[0]

    time_register = re.findall(r'<li><em>注册时间</em>(.*?)</li>', resp.content)[0]
    time_last_login = re.findall(r'<li><em>上次活动时间</em>(.*?)</li>', resp.content)[0]

    login_count = ''

    count_post = re.findall(r'主题数 (.*?)<', resp.content)[0]
    count_reply = re.findall(r'回帖数 (.*?)<', resp.content)[0]

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