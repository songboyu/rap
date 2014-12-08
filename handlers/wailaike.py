# -*- coding: utf-8 -*-
"""外来客回复模块

@author: kerry
@since: 2014-12-2
@summary: 外来客论坛

@var CHARSET: 外来客网页编码
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
def login_wailaike(sess, src):
    """ 外来客社区登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    # Step 1: Login
    #登录页面
    login_page = 'http://www.wailaike.net/'
    resp = sess.get(
        login_page + 'login_g')
    #获取登录页面content的HTML
    soup = BeautifulSoup(resp.content)
    #查找与{'name': 'login'}匹配的form标签
    form = soup.find('form', attrs={'id': 'logForm'})
    #将form标签中的form属性内容存入payload中
    payload = utils.get_datadic(form)

    resp = sess.get(
        'http://www.wailaike.net/pass.php')
    payload['time'] = re.findall('"time":"(.*?)"', resp.content)[0]

    payload = {
        'email': 'cangchedaobo3@163.com',
        'password': payload['time'],
        'passwordFake': 'wenshen4921119',
        'redirect_to': 'http://www.wailaike.net/'
    }

    #发送post包
    resp = sess.post(login_page + form['action'], data=payload)
    soup = BeautifulSoup(resp.content)

    #判断登录后页面是否含有用户字段，若存在则证明登录成功，否则失败
    if '注册' not in resp.content:
    #if u'站内信'.encode(CHARSET) in resp.content:
        return True
    return False

def post_wailaike_forum(post_url, src):
    """ 外来客论坛发主贴函数

    @param post_url:   板块地址 如：http://www.wailaike.net/newpost?gid=1
    @type post_url:    str

    @param src:        用户名，密码，标题，主帖内容，等等。用户名：cangchedaobo3@163.com 密码：wenshen4921119
    @type src:         dict

    @return:           是否发帖成功，帖子URL
    @rtype:            bool,str

    """
     # Returnable logger
    logger = utils.RAPLogger(post_url)
    host = utils.get_host(post_url)
    sess = utils.RAPSession(src)

    # Step 1: 登录
    if not login_wailaike(sess, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.info(' Login OK')
    gid = re.findall(r'gid=(\d*)', post_url)[0]
    resp = sess.get('http://www.wailaike.net/newpost?gid='+gid)
    soup = BeautifulSoup(resp.content)
    # 获得发帖form
    form = soup.find('form', attrs={'id': 'editor'})
    # 构造回复参数
    payload = utils.get_datadic(form)
    payload['title'] = src['subject'].decode('utf8').encode(CHARSET)
    payload['rstbody'] = src['content'].decode('utf8').encode(CHARSET)

    resp = sess.get('http://www.wailaike.net/time.php')
    payload['time'] = re.findall('"time":"(.*?)"', resp.content)[0]

    # 发送发帖post包
    resp = sess.post('http://www.wailaike.net/newpost?gid='+gid, data=payload)

    # print resp.content.decode(CHARSET)
    # 若指定字样出现在response中，表示发帖成功
    if src['subject'] not in resp.content:
        logger.error(' Post Error')
        return (False, '', str(logger))
    logger.info(' Post OK')
    resp = sess.get('http://www.wailaike.net/group_post?gid='+gid)
    url1 = re.findall(r'<h3 class="titles-txt"><a href=\"(.*?)\" target="_blank">'+src['subject']+'</a></h3>',resp.content)[0]
    url = "http://www.wailaike.net"+url1
    logger.info(url)
    return (True, url, str(logger))


