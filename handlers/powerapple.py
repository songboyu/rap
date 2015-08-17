# -*- coding: utf-8 -*-
"""超级苹果回复模块

@author: kerry & sky
@since: 2014-10-25
@summary: 超级苹果论坛，超级苹果新闻
"""

from bs4 import BeautifulSoup
from hashlib import md5
from utils import *
import time
import re
import utils

def login_powerapple(sess, src):
    """ 超级苹果社区登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """

 # Step 1: Login
    #登录页面
    login_page = 'http://bbs.powerapple.com/'
    resp = sess.get(
        login_page + '/member.php?mod=logging&action=login')
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
    if src['username'] in resp.content:
        return True
    return False

# Coding: utf8
# Captcha: arithmetic
# Login: required
def reply_powerapple_forum(post_url, src):

     # Returnable logger
    logger = utils.RAPLogger(post_url)
    host = utils.get_host(post_url)
    sess = utils.RAPSession(src)

    # Step 1: 登录
    if not login_powerapple(sess, src):
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
        logger.info('Reply OK')
    else:
        logger.error('Reply Error: please try again !')
        return (False, str(logger))
    return (True, str(logger))

def post_powerapple_forum(post_url, src):
    """ 超级苹果论坛发主贴函数

    @param post_url:   板块地址 如：http://bbs.powerapple.com/forum.php?mod=forumdisplay&fid=50
    @type post_url:    str

    @param src:        用户名，密码，标题，主帖内容，等等。
    @type src:         dict

    @return:           是否发帖成功，帖子URL
    @rtype:            bool,str

    """
    logger = utils.RAPLogger(post_url)
    host = utils.get_host(post_url)
    sess = utils.RAPSession(src)

    # Step 1: 登录
    if not login_powerapple(sess, src):
        logger.error(' Login Error')
        return ('', str(logger))
    logger.info(' Login OK')
    # Step 2: Load post page
    fid = re.findall(r'fid=(\d+)', post_url)[0]
    # 获取所需发帖页面，查找与{'id':'fastpostform'}匹配的form标签
    resp = sess.get('http://bbs.powerapple.com/forum.php?mod=post&action=newthread&fid='+fid)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'postform'})

    # Step 3: Submit
    # 回复内容
    payload = get_datadic(form)
    payload['subject'] = src['subject']
    payload['message'] = src['content']
    payload['typeid'] = '138'
    #发送post包
    resp = sess.post(host + form['action'], data=payload)
    #获取回帖页面content的HTML

    print_to_file(resp.content)
    #判断回帖后页面是否含有回帖内容，若存在则证明回帖成功，否则失败
    if src['subject'] in resp.content:
        logger.info('Post OK')
    else:
        logger.error('Reply Error: please try again !')
        return ('', str(logger))
    return (resp.url, str(logger))


# Coding: utf8
# Captcha: required
# Login: not required
def reply_powerapple_news(post_url, src):
    """超级苹果新闻回帖模块
    @author: sky
    @since: 2014-11-11

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   帖子地址
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool
    """
    if src['TTL'] == 0:
        raise RAPMaxTryException('captcha')
    logger = RAPLogger(post_url)

    host = get_host(post_url)
    sess = RAPSession(src)

    # Step 1: 获取回帖页面
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    # Step 2: 验证码
    # 获取验证码图片
    resp = sess.get(host + 'captcha',
    headers={
        'Accept': config.accept_image,
        'Referer': post_url
    },
    params={'type': '', 'time': time.time()*1000})
    # 获取验证码字符串              
    seccode = crack_captcha(resp.content)
    logger.info(' seccode:' + seccode)

    # Step 3: 提交回帖
    # 回复内容
    form = soup.find('form', attrs={'class': 'new_comment'})
    payload = get_datadic(form)
    payload['captcha'] = seccode
    payload['comment[content]'] = src['content']
    #发送post包
    resp = sess.post(host + form['action'], data=payload)
    # #再次请求原网页，查看是否已经有回帖内容
    # resp = sess.get(post_url)
    #判断回帖后页面是否含有回帖内容，若存在则证明回帖成功，否则失败
    if src['content'] in resp.content:
        logger.info('Reply OK')
    else:
        logger.error('Login Error: Reply Error, please try again !')
        return (False, str(logger))
    return (True, str(logger))

def get_account_info_powerapple_forum(src):
    """ 超级苹果账户信息获取函数

    @param src:        用户名，密码
    @type src:         dict

    @return:           账户信息
    @rtype:            dict
    """
    logger = utils.RAPLogger(src['username'])
    sess = utils.RAPSession(src)

    # Step 1: 登录
    if not login_powerapple(sess, src):
        logger.error(' Login Error')
        return ({}, str(logger))
    logger.info(' Login OK')

    resp = sess.get('http://bbs.powerapple.com/home.php?mod=space&do=profile')

    soup = BeautifulSoup(resp.content)
    head_image = soup.select('a.avtm img')[0]['src']

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
