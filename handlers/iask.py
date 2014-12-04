# -*- coding: utf-8 -*-
"""凯迪回复模块

@author: HSS
@since: 2014-12-03
@summary: 加拿大家园

"""
from bs4 import BeautifulSoup
from utils import *

def login_iask(sess, src):
    """ 加拿大家园登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    host = 'http://forum.iask.ca/'
    resp = sess.get(host)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id': 'login'})

    payload = get_datadic(form)
    payload['login'] = src['username']
    payload['password'] = src['password']
    # 发送登录post包
    resp = sess.post(host + form['action'], data=payload)
    # 若指定字样出现在response中，表示登录成功
    if src['username'] not in resp.content:
        return False
    return True

def post_iask_forum(post_url, src):
    """ 加拿大家园论坛发主贴模块

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   板块地址
    @type post_url:    str

    @param src:        用户名，密码，标题，帖子内容等等。
    @type src:         dict

    @return:           是否发帖成功，url
    @rtype:            bool,str

    """
    logger = RAPLogger(post_url)
    sess = RAPSession(src)
    # Step 1: 登录
    if not login_iask(sess, src):
        logger.error(' Login Error')
        return (False, '', str(logger))
    logger.info(' Login OK')

    host = 'http://forum.iask.ca/'
    page_url = post_url + 'create-thread'
    resp = sess.get(page_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id': 'ThreadCreate'})

    payload = get_datadic(form)
    payload['title'] = src['subject']
    payload['message_html'] = '<p>'+src['content']+'</p>'
    payload['_xfRequestUri'] = page_url[20:]
    payload['poll[max_votes_type]'] = 'single'
    payload['_xfNoRedirect'] = '1'
    payload['_xfResponseType'] = 'json'
    payload['watch_thread_state'] = '0'

    print payload
    # 发送登录post包
    resp = sess.post(host + form['action'], data=payload,
                     headers = {
                         'Accept':'application/json, text/javascript, */*; q=0.01',
                         'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                         'Referer':page_url,
                         'X-Ajax-Referer':page_url,
                         'X-Requested-With':'XMLHttpRequest'
                     })
    print resp.url
    print resp.content
    if src['subject'] not in resp.content:
        logger.error(' Post Error')
        return (False, '', str(logger))
    logger.info(' Post OK')
    url = resp.url
    print url
    return (True, url, str(logger))