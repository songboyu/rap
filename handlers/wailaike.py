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

    @param post_url:   板块地址 如：http://www.wailaike.net/group_post?gid=1
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
        return ('', str(logger))
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
        return ('', str(logger))
    logger.info(' Post OK')
    resp = sess.get('http://www.wailaike.net/group_post?gid='+gid)
    url1 = re.findall(r'<h3 class="titles-txt"><a href=\"(.*?)\" target="_blank">'+src['subject']+'</a></h3>',resp.content)[0]
    url = "http://www.wailaike.net"+url1
    return (url, str(logger))


def get_account_info_wailaike_forum(src):
    """ 网易论坛账户信息获取函数

    @param src:        用户名，密码
    @type src:         dict

    @return:           账户信息
    @rtype:            dict
    """
    logger = utils.RAPLogger(src['username'])
    sess = utils.RAPSession(src)

    # Step 1: 登录
    if not login_wailaike(sess, src):
        logger.error(' Login Error')
        return ({}, str(logger))
    logger.info(' Login OK')

    resp = sess.get('http://www.wailaike.net/index.php')
    # f = open('1.html','w')
    # f.write(resp.content)
    # f.close()
    id_count = re.findall(r'/user_page\?i=(\d+)', resp.content)
    # id_count = re.findall(r'<a href="/user_page?i=(.*?)" class="s_menu-title-hover">', resp.content)
    print id_count[0]

    #resp = sess.get('http://www.wailaike.net/user_page?i='+str(id_count[0]))

    head_image = ''

    account_score = ''
    account_class = ''

    time_register = ''
    time_last_login = ''
    login_count = ''
    count_reply = ''

    count = -1
    count_post = 0
    resp = sess.get('http://www.wailaike.net/user_page?i='+id_count[0])
    count = len(re.findall(r'index-brief-main', resp.content))
    count_post = count_post + count
    print count_post
    #  page = page + 1

    # count = -1
    # page = 1
    # count_reply = 0
    # while count != 0:
    #     resp = sess.get('http://bbs.163.com/user/reply.do?page='+str(page))
    #     count = len(re.findall(r'my_bbs_title', resp.content))
    #     count_reply = count_reply + count
    #     page = page + 1

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