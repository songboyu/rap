# -*- coding: utf-8 -*-
"""倍可亲回复模块

@author: kerry
@since: 2014-10-25
@summary: 倍可亲论坛

@var CHARSET: 倍可亲网页编码
@type CHARSET: str
"""

import re
from hashlib import md5

from bs4 import BeautifulSoup

import utils

CHARSET = 'utf-8'

# Coding: utf8
# Captcha: arithmetic
# Login: required
def login_backchina(sess, src):
    """ 倍可亲社区登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    # Step 1: Login
    #登录页面
    login_page = 'http://www.backchina.com/'
    resp = sess.get(
        login_page + '/member.php?mod=logging&action=login&referer=')
    #获取登录页面content的HTML
    soup = BeautifulSoup(resp.content)
    #查找与{'name': 'login'}匹配的form标签
    form = soup.find('form', attrs={'name': 'login'})
    #将form标签中的form属性内容存入payload中
    payload = utils.get_datadic(form)

    #将src['username']内容，src['password']加密后内容存入payload中
    payload['username'] = src['username']
    payload['password'] = md5(src['password']).hexdigest()

    #发送post包
    resp = sess.post(login_page + form['action'], data=payload)
    soup = BeautifulSoup(resp.content)

    #判断登录后页面是否含有用户字段，若存在则证明登录成功，否则失败
    if src['username'] in resp.content:
        #id_count = re.findall(r'a class="eis_ttbat" href=\"http://www.backchina.com/u/(.*?)\">', resp.content)
        #print id_count
        return True
    return False

def reply_backchina_forum(post_url, src):
    """倍可亲回复模块

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   帖子地址
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """


    # Returnable logger
    logger = utils.RAPLogger(post_url)
    host = utils.get_host(post_url)
    sess = utils.RAPSession(src)

    # Step 1: 登录
    if not login_backchina(sess, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.info(' Login OK')

    # Step 2: Load post page
    # 获取所需发帖页面，查找与{'id':'fastpostform'}匹配的form标签
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'fastpostform'})

    # Step 3: Submit
    # 回复内容
    payload = utils.get_datadic(form)
    if 'subject' in src:    
        payload['subject'] = src['subject']
    payload['message'] = src['content']

    #发送post包
    resp = sess.post(host + form['action'], data=payload)
    #获取回帖页面content的HTML
    soup = BeautifulSoup(resp.content)

    #判断回帖后页面是否含有回帖内容，若存在则证明回帖成功，否则失败
    if src['content'] in resp.content:
        logger.info('Reply OK')
    else:
        logger.error('Reply Error: Reply Error, please try again !')
        return (False, str(logger))
    return (True, str(logger))


def get_account_info_backchina_forum(src):
    """ 倍可亲账户信息获取函数

    @param src:        用户名，密码
    @type src:         dict

    @return:           账户信息
    @rtype:            dict
    """
    logger = utils.RAPLogger(src['username'])
    sess = utils.RAPSession(src)

    faild_info = {'Error':'Failed to get account info'}
    # Step 1: 登录
    if not login_backchina(sess, src):
        logger.error(' Login Error')
        return (faild_info, str(logger))
    logger.info(' Login OK')

    resp = sess.get('http://www.backchina.com/special/bbs/')
    id_count = re.findall(r'<a href="http://www.backchina.com/u/(.*?)" class="eis_ttbat">', resp.content)

    resp = sess.get('http://www.backchina.com/home.php?mod=space&uid='+str(id_count[0])+'&do=profile')

    head_image = 'http://backchina-member.com/ucenter/images/noavatar_middle.gif'
    account_score = re.findall(r'<li><em>积分</em>(.*?)</li>', resp.content)[0]
    #print str(account_score[0])
    account_class = ''

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
    return (account_info, str(logger))