# -*- coding: utf-8 -*-
"""倍可亲回复模块

@author: kerry
@since: 2014-10-25
@summary: 倍可亲论坛

@var CHARSET: 倍可亲网页编码
@type CHARSET: str
"""
from bs4 import BeautifulSoup
from hashlib import md5
from utils import get_datadic
from utils import get_host
fromutils import RAPSession
from utils import RAPLogger

# Coding: utf8
# Captcha: arithmetic
# Login: required
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
    logger = RAPLogger(post_url)

    host = get_host(post_url)
    sess = RAPSession(src)

    # Step 1: Login
    #登录页面
    resp = sess.get(
        host + '/member.php?mod=logging&action=login&referer=')
    #获取登录页面content的HTML
    soup = BeautifulSoup(resp.content)
    #查找与{'name': 'login'}匹配的form标签
    form = soup.find('form', attrs={'name': 'login'})
    #将form标签中的form属性内容存入payload中
    payload = get_datadic(form)

    #将src['username']内容，src['password']加密后内容存入payload中
    payload['username'] = src['username']
    payload['password'] = md5(src['password']).hexdigest()

    #发送post包
    resp = sess.post(host + form['action'], data=payload)
    soup = BeautifulSoup(resp.content)

    #判断登录后页面是否含有用户字段，若存在则证明登录成功，否则失败
    if src['username'] in resp.content:
        logger.debug('Login OK')
    else:
        logger.error(
            'Login Error: Username Or Password error , please try again !')
        return (False, str(logger))

    # Step 2: Load post page
    # 获取所需发帖页面，查找与{'id':'fastpostform'}匹配的form标签
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'fastpostform'})

    # Step 3: Submit
    # 回复内容
    payload = get_datadic(form)
    if 'subject' in src:
        payload['subject'] = src['subject']
    payload['message'] = src['content']

    #发送post包
    resp = sess.post(host + form['action'], data=payload)
    #获取回帖页面content的HTML
    soup = BeautifulSoup(resp.content)

    #判断回帖后页面是否含有回帖内容，若存在则证明回帖成功，否则失败
    if src['content'] in resp.content:
        logger.debug('Reply OK')
    else:
        logger.error('Login Error: Reply Error, please try again !')
        return (False, str(logger))
    return (True, str(logger))
