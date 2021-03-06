# -*- coding: utf-8 -*-
"""消息树模块

@author: HSS
@since: 2014-10-20
@summary: 消息树

@var CHARSET: 消息树网页编码
@type CHARSET: str

"""
import re

from bs4 import BeautifulSoup

import time
import utils

CHARSET = 'gbk'
def login_enewstree(post_url, sess, src):
    """ 消息树登录函数

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
    payload['username'] = src['username'].decode('utf8').encode(CHARSET,'ignore')
    payload['password'] = src['password'].decode('utf8').encode(CHARSET,'ignore')
    # 发送登录post包
    resp = sess.post('http://enewstree.com/discuz/'+form['action'], data=payload,
                     headers = {
                         'Referer':post_url
                     })
    # 若指定字样出现在response中，表示登录成功
    if src['username'].decode('utf8') not in resp.content.decode(CHARSET,'ignore'):
        return False
    return True

def reply_enewstree_forum(post_url, src):
    """ 消息树回复函数

        - Name:     凯迪社区
        - Feature:  club.kdnet.net
        - Captcha:  NO
        - Login:    NO

    @param post_url:   帖子地址
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否回复成功
    @rtype:            bool

    """
    logger = utils.RAPLogger(post_url)
    sess = utils.RAPSession(src)
    # Step 1: 登录
    if not login_enewstree(post_url, sess, src):
        logger.error(' Login Error')
        return ('', str(logger))
    logger.info(' Login OK')

    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    # 获得回复form
    form = soup.find('form', attrs={'id': 'fastpostform'})
    # 构造回复参数
    payload = utils.get_datadic(form)
    payload['message'] = src['content'].decode('utf8').encode(CHARSET,'ignore'),

    resp = sess.post('http://enewstree.com/discuz/'+form['action'],
                     data=payload,
                     headers = {
                         'Referer':post_url
                     })
    if src['content'].decode('utf8') not in resp.content.decode(CHARSET,'ignore'):
        logger.error(' Reply Error')
        return (False, str(logger))
    logger.info(' Reply OK')
    return (True, str(logger))

def post_enewstree_forum(post_url, src):
    """ 消息树发主贴函数

    @param post_url:   板块地址 如：http://enewstree.com/discuz/forum.php?mod=forumdisplay&fid=47
    @type post_url:    str

    @param src:        用户名，密码，标题，主帖内容，等等。
    @type src:         dict

    @return:           是否发帖成功，帖子URL
    @rtype:            bool,str

    """
    logger = utils.RAPLogger(post_url)
    sess = utils.RAPSession(src)
    # Step 1: 登录
    if not login_enewstree(post_url, sess, src):
        logger.error(' Login Error')
        return ('', str(logger))
    logger.info(' Login OK')

    fid = re.findall(r'fid=(\d*)', post_url)[0]
    resp = sess.get('http://enewstree.com/discuz/forum.php?mod=post&action=newthread&fid='+fid)
    formhash = re.findall(r'formhash=(.*?)"', resp.content)[0]
    logger.info('formhash:'+ formhash)
    payload = {
        'formhash':formhash,
        'posttime':int(time.time()),
        'wysiwyg':'1',
        'subject':src['subject'].decode('utf8').encode(CHARSET,'ignore'),
        'message':src['content'].decode('utf8').encode(CHARSET,'ignore'),
        'allownoticeauthor':'1',
        'usesig':'1',
        'secqaahash':'qSxqZkkW',
        'secanswer':'1776',
        'seccodehash':'cSxqZkkW',
        'seccodemodid':'forum::post',
        'seccodeverify':'ec48',
        'save':'',
        'uploadalbum':'-2',
        'newalbum':'',
    }

    # 发送登录post包
    resp = sess.post('http://enewstree.com/discuz/forum.php?mod=post&action=newthread&fid='+fid
                     +'&extra=&topicsubmit=yes',
                     data=payload,
                     headers = {
                         'Referer':post_url
                     })
    utils.print_to_file(resp.content)
    # 若指定字样出现在response中，表示回复成功
    if src['subject'].decode('utf8') not in resp.content.decode(CHARSET):
        logger.error(' Post Error')
        return ('', str(logger))
    logger.info(' Post OK')
    url = resp.url
    print url
    return (url, str(logger))

def get_account_info_enewstree_forum(src):
    """ 消息树账户信息获取函数

    @param src:        用户名，密码
    @type src:         dict

    @return:           账户信息
    @rtype:            dict
    """
    logger = utils.RAPLogger(src['username'])
    sess = utils.RAPSession(src)
    post_url='http://enewstree.com/discuz/forum.php'

    # Step 1: 登录
    if not login_enewstree(post_url,sess, src):
        logger.error(' Login Error')
        return ({}, str(logger))
    logger.info(' Login OK')

    resp = sess.get('http://enewstree.com/discuz/home.php?mod=space&do=profile')

    html = resp.content.decode(CHARSET).encode('utf8')

    soup = BeautifulSoup(resp.content)
    head_image = soup.select('a.avtm img')[0]['src']

    account_score = re.findall(r'<li><em>积分</em>(.*?)</li>', html)[0]
    account_class = re.findall(r'ac=usergroup.*>(.*?)</a>', html)[0]

    time_register = re.findall(r'<li><em>注册时间</em>(.*?)</li>', html)[0]
    time_last_login = re.findall(r'<li><em>上次活动时间</em>(.*?)</li>', html)[0]

    login_count = ''

    count_post = re.findall(r'主题数 (.*?)<', html)[0]
    count_reply = re.findall(r'回帖数 (.*?)<', html)[0]

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