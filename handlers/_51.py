# -*- coding: utf-8 -*- 

import requests, re, random, logging
from bs4 import BeautifulSoup

import config
from utils import *
import utils
from utils import get_datadic

# Coding: utf8
# Captcha: not required
# Login: required
def login_51_forum(post_url, s, src):
    """51资讯论坛登录模块

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    host = get_host(post_url)
    
    r = s.get(host + 'logging.php?action=login')
    soup = BeautifulSoup(r.content)
    form = soup.find('form', attrs={'name': 'login'})
    payload = get_datadic(form)
    payload['username'] = src['username']
    payload['password'] = src['password']
    payload['fastloginfield'] = 'username'
    r = s.post(host + form['action'] + '&inajax=1', data=payload)
    # 若指定字样出现在response中，表示登录成功
    if '欢迎您回来' not in r.content:
        return False
    return True

def reply_51_forum(post_url, src):
    
    logger = utils.RAPLogger(post_url)
    host = utils.get_host(post_url)
    s = utils.RAPSession(src)

    # 登录
    if not login_51_forum(post_url, s, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.info(' Login OK')

    r = s.get(post_url)
    soup = BeautifulSoup(r.content)
    form = soup.find('form', attrs={'id': 'fastpostform'})
    payload = get_datadic(form)
    payload['message'] = src['content']
    r = s.post(host + form['action'] + '&inajax=1', data=payload)
    if '对不起' in r.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))

# Coding: utf8
# Captcha: not required
# Login: required
def post_51_forum(post_url, src):
    """51资讯论坛发主贴模块

    @author: sky
    @since: 2014-12-01

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   帖子地址  http://bbs.51.ca/forumdisplay.php?fid=40
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    logger = utils.RAPLogger(post_url)
    s = utils.RAPSession(src)

    # 登录
    if not login_51_forum(post_url, s, src):
        logger.error(' Login Error')
        return ('', str(logger))
    logger.info(' Login OK')

    fid = re.findall(r'fid=(\d*)', post_url)[0]
    resp = s.get('http://bbs.51.ca/post.php?action=newthread&fid='+fid)
    soup = BeautifulSoup(resp.content)
    # 获得发帖form表单
    form = soup.find('form', attrs={'id': 'postform'})

    # 构造回复参数
    payload = get_datadic(form)
    payload['posttime'] = random.randint(1000000000,9999999999)
    payload['wysiwyg'] = '1'
    payload['subject'] = src['subject']
    payload['message'] = src['content']

    #发送发主贴post包
    resp = s.post('http://bbs.51.ca/post.php?action=newthread&fid='+fid+'&extra=&topicsubmit=yes', data=payload)
    # 若指定字样出现在response中，表示发帖成功
    if src['subject'] not in resp.content:
        logger.error(' Post Error')
        return ('', str(logger))
    logger.info(' Post OK')
    url = resp.url
    print url
    return (url, str(logger))
    

def get_account_info_51_forum(src):
    logger = utils.RAPLogger('51=>' + src['username'])
    sess = utils.RAPSession(src)

    # Step 1: 登录
    if not login_51_forum('http://bbs.51.ca/', sess, src):
        logger.error(' Login Error')
        return ({}, str(logger))
    logger.info(' Login OK')

    resp = sess.get('http://bbs.51.ca/')
    info_url = re.findall('(space-uid-\d+\.html)', resp.content)[0]
    resp = sess.get('http://bbs.51.ca/' + info_url)

    head_image = re.findall('avatar"><img src="(.*?)"', resp.content)[0]
    account_score = int(re.findall('积分: (\d+?)<', resp.content)[0])
    account_class = re.findall('color="#33C">(.*?)<', resp.content)[0]
    time_register = re.findall('注册日期: (.*?)<', resp.content)[0]
    time_last_login = re.findall('上次访问: <span title="(.*?)"', resp.content)[0]
    login_count = 0
    count_post = int(re.findall('帖子: (\d+?) 篇', resp.content)[0])
    count_reply = 0

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
