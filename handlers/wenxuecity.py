# -*- coding: utf-8 -*- 

import requests, re, random, logging
from bs4 import BeautifulSoup

import config
from utils import *
import utils

def login_wenxuecity(s, src):
    payload = {
        'redirect': 'http://bbs.wenxuecity.com/',
        'username': src['username'],
        'password': src['password'],
        'login': '登录',
    }
    # Terminate the endless redirection, reload the page instead to check success.
    r = s.post('http://bbs.wenxuecity.com/members/passport.php?act=topbar_post&iframe=0', data=payload, allow_redirects=False)
    r = s.get('http://passport.wenxuecity.com/members/script/members.php')
    if 'login_in_box' not in r.content:
        return False
    return True

# Coding: utf8
# Captcha: not required
# Login: required
def reply_wenxuecity_forum(post_url, src):
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    s = RAPSession(src)

    # Since subject is mandatory, we take first few words as default subject.
    if 'subject' not in src:
        src['subject'] = src['content'].decode('utf8')[:15].encode('utf8')

    if not login_wenxuecity(s, src):
        logger.error('Login Error')
        return (False, str(logger))
    logger.info('Login OK')

    r = s.get(post_url)
    soup = BeautifulSoup(r.content)
    form = soup.find('form', attrs={'id': 'postform'})
    payload = get_datadic(form)
    payload['title'] = src['subject']
    payload['msgbodytext'] = src['content']
    # How to confirm reply OK?
    # Terminate the endless redirection, reload the page instead to check success.
    r = s.post(host + form['action'], data=payload, allow_redirects=False)
    r = s.get(post_url)
    if src['content'] not in r.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))

# Coding: utf8
# Captcha: not required
# Login: required
def reply_wenxuecity_news(post_url, src):
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    s = RAPSession(src)

    if not login_wenxuecity(s, src):
        logger.error('Login Error')
        return (False, str(logger))
    logger.info('Login OK')

    r = s.get(post_url)
    soup = BeautifulSoup(r.content)
    # If this is news page, then go to comment page.
    if 'act=comment' not in post_url:
        post_url = host + soup.find('div', attrs={'class': 'postcomment'}).find('a')['href']
        r = s.get(post_url)
        soup = BeautifulSoup(r.content)

    form = soup.find('form', attrs={'id': 'postform'})
    payload = get_datadic(form)
    payload['msgbody'] = src['content']
    r = s.post(host + 'news' + form['action'].strip('.'), data=payload)
    # Reload the page to check success.
    r = s.get(post_url)
    if src['content'] not in r.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))

# Coding: utf8
# Captcha: not required
# Login: required
def reply_wenxuecity_blog(post_url, src):
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    s = RAPSession(src)

    if not login_wenxuecity(s, src):
        logger.error('Login Error')
        return (False, str(logger))
    logger.info('Login OK')

    r = s.get(post_url)
    soup = BeautifulSoup(r.content)
    form = soup.find('form', attrs={'action': '/blog/index.php?act=commentAdd'})
    payload = get_datadic(form)
    payload['postcomments'] = src['content']
    # Terminate the endless redirection, reload the page instead to check success.
    r = s.post(host + form['action'], data=payload, allow_redirects=False)
    r = s.get(post_url)
    if src['content'] not in r.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))


# Coding: utf8
# Captcha: not required
# Login: required
def post_wenxuecity_blog(post_url, src):
    """文学城博客发主贴模块

    @author: sky
    @since: 2014-11-28

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   帖子地址 http://blog.wenxuecity.com
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    logger = utils.RAPLogger(post_url)
    host = utils.get_host(post_url)
    s = utils.RAPSession(src)

    # 登录
    if not login_wenxuecity(s, src):
        logger.error(' Login Error')
        return ('', str(logger))
    logger.info(' Login OK')

    # 获得发帖form表单
    resp = s.get('http://blog.wenxuecity.com/blog/blogctl.php?act=articleAdd')
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'name': 'newblog'})

    # 构造回复参数
    payload = utils.get_datadic(form)
    payload['title'] = src['subject']
    payload['content'] = src['content']

    #发送发主贴post包
    resp = s.post(host + form['action'], data=payload, allow_redirects=False)
    # url
    resp = s.get('http://passport.wenxuecity.com/members/script/members.php')
    blog_url = re.findall(r'<a href="(.*?)">我的博客',resp.content)[0]
    resp = s.get(blog_url)
    # 若指定字样出现在response中，表示发帖成功
    if src['subject'] not in resp.content:
        logger.error(' Post Error')
        return ('', str(logger))
    logger.info(' Post OK')
    href = re.findall(r'<div class="menuCell_main">[\s|\S]*?<a href="(.*?)">[\s|\S]*?<span>'+src['subject'], resp.content)[0]
    url = host + href
    return (url, str(logger))
    

def get_account_info_wenxuecity_blog(src):
    logger = utils.RAPLogger('wenxuecity=>' + src['username'])
    sess = utils.RAPSession(src)

    # Step 1: 登录
    if not login_wenxuecity(sess, src):
        logger.error('Login Error')
        return ({}, str(logger))
    logger.info('Login OK')

    resp = sess.get('http://bbs.wenxuecity.com/members/')
    soup = BeautifulSoup(resp.content)
    head_image = 'http://www.wenxuecity.com' + soup.select('img#preview')[0]['src']
    time_last_login = re.findall('最后登录：(.+?)<', resp.content)[0]
    login_count = re.findall('登录次数 : </strong>(\d+?)<', resp.content)[0]

    uid = re.findall('myoverview/(\d+)', resp.content)[0]
    resp = sess.get('http://blog.wenxuecity.com/myoverview/' + uid)
    html = resp.content
    result = re.findall('我的文章.*?\((\d+?)\)', html, re.S)
    if len(result) == 0:
        count_post = 0
    else:
        count_post = int(result[0])

    # 被回复数 代替 回复数
    page = -1
    count_reply = 0
    while True:
        page += 1
        resp = sess.get('http://blog.wenxuecity.com/blog/frontend.php?page=%d&act=articleHome&blogId=%s' % (page, uid))
        result = re.findall('评论</a>.*?<em>\((\d+)\)', resp.content, re.S)
        count_per_page = sum([int(x) for x in result])
        if count_per_page == 0: break
        count_reply += count_per_page

    # 博客访问量 代替 积分
    count_js = re.findall('(http://count.wenxuecity.com.*?true)"', html)[0]
    resp = sess.get(count_js)
    result = re.findall("'(.*)'", resp.content)
    if len(result) == 0:
        account_score = 0
    else:
        txt = result[0]
        account_score = int(txt.replace(',', ''))
    # 无等级
    account_class = '无'
    # 无注册时间
    time_register = ''


    account_info = {
        #########################################
        # 用户名
        'username': src['username'],
        # 密码
        'password': src['password'],
        # 头像图片
        'head_image': head_image,
        #########################################
        # 积分
        'account_score': account_score,
        # 等级
        'account_class': account_class,
        #########################################
        # 注册时间
        'time_register': time_register,
        # 最近登录时间
        'time_last_login': time_last_login,
        # 登录次数
        'login_count': login_count,
        #########################################
        # 主帖数
        'count_post': count_post,
        # 回复数
        'count_reply': count_reply,
        #########################################
    }
    logger.info('Get account info OK')
    return (account_info, str(logger))
