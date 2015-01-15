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
        return (False, str(logger))
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
        return (False, '', str(logger))
    logger.info(' Post OK')
    href = re.findall(r'<div class="menuCell_main">[\s|\S]*?<a href="(.*?)">[\s|\S]*?<span>'+src['subject'], resp.content)[0]
    url = host + href
    return (True, url, str(logger))
    

