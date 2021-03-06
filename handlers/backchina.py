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
import urllib
import time
import binascii

from bs4 import BeautifulSoup

import utils

CHARSET = 'utf8'

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
    #判断登录后页面是否含有用户字段，若存在则证明登录成功，否则失败
    if u'自动跳转' in resp.content.decode('utf8'):
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

    #判断回帖后页面是否含有回帖内容，若存在则证明回帖成功，否则失败
    if src['content'] in resp.content:
        logger.info('Reply OK')
    else:
        logger.error('Reply Error: Reply Error, please try again !')
        return (False, str(logger))
    return (True, str(logger))

def post_backchina_forum(post_url, src):
    """ 倍可亲论坛发主贴函数

    @param post_url:   板块地址 如：http://www.backchina.com/forum/37/index-1.html
    @type post_url:    str

    @param src:        用户名，密码，标题，主帖内容，等等。
    @type src:         dict

    @return:           是否发帖成功，帖子URL
    @rtype:            bool,str

    """
    # Returnable logger
    logger = utils.RAPLogger(post_url)
    sess = utils.RAPSession(src)

    # Step 1: 登录
    if not login_backchina(sess, src):
        logger.error(' Login Error')
        return ('', str(logger))
    logger.info(' Login OK')

    fid = re.findall(r'forum/(\d+)/', post_url)[0]
    resp = sess.get('http://www.backchina.com/forum.php?mod=post&action=newthread&fid='+fid)
    soup = BeautifulSoup(resp.content)
    # 获得发帖form
    form = soup.find('form', attrs={'id': 'postform'})
    # 构造回复参数
    payload = utils.get_datadic(form)
    payload['subject'] = src['subject']
    payload['message'] = src['content']
    # 发送发帖post包
    resp = sess.post('http://www.backchina.com/forum.php?mod=post&action=newthread&fid='+fid+'&extra=&topicsubmit=yes', data=payload)

    # 若指定字样出现在response中，表示发帖成功
    if src['subject'] not in resp.content:
        logger.error(' Post Error')
        return ('', str(logger))
    logger.info(' Post OK')
    url = resp.url
    return (url, str(logger))


def get_account_info_backchina_forum(src):
    """ 倍可亲账户信息获取函数

    @param src:        用户名，密码
    @type src:         dict

    @return:           账户信息
    @rtype:            dict
    """
    logger = utils.RAPLogger(src['username'])
    sess = utils.RAPSession(src)

    # Step 1: 登录
    if not login_backchina(sess, src):
        logger.error(' Login Error')
        return ({}, str(logger))
    logger.info(' Login OK')

    resp = sess.get('http://www.backchina.com/home.php?mod=space&do=profile')

    soup = BeautifulSoup(resp.content)
    head_image = soup.select('a.avtm img')[0]['src']

    account_score = re.findall(r'<li><em>积分</em>(.*?)</li>', resp.content)[0]
    account_class = re.findall(r'ac=usergroup.*>(.*?)</a>', resp.content)[0]

    time_register = re.findall(r'<li><em>注册时间</em>(.*?)</li>', resp.content)[0]
    time_last_login = re.findall(r'<li><em>上次活动时间</em>(.*?)</li>', resp.content)[0]

    login_count = 0

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


def upload_head_backchina_forum(src):
    logger = utils.RAPLogger('Upload head 51_forum=>' + src['username'])
    sess = utils.RAPSession(src)

    # Step 1: 登录
    if not login_backchina(sess, src):
        logger.error('Login Error')
        return ('', str(logger))
    logger.info('Login OK')

    resp = sess.get('http://www.backchina.com/home.php?mod=spacecp&ac=avatar')
    input = urllib.unquote(re.findall(r'input=(.*?)&',resp.content)[0])
    agent = re.findall(r'agent=(.*?)&',resp.content)[0]
    head_url = re.findall(r'<td><img src="(.*?)"',resp.content)[0]
    print 'input:',input
    print 'agent:',agent

    avatar1 = binascii.hexlify(open(src['head'],'rb').read()).upper()
    avatar2 = avatar1
    avatar3 = avatar1

    params = {
        'm':'user',
        'inajax':'1',
        'a':'rectavatar',
        'appid':'14',
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
    resp = sess.post('http://backchina-member.com/ucenter/index.php', data=payload, params=params)


    print resp.content
    if 'success="1"' in resp.content:
        logger.info('uploadavatar OK')
        return (head_url, str(logger))
    else:
        logger.info('uploadavatar Error')
        return ('', str(logger))
