# -*- coding: utf-8 -*-
"""纽约华人资讯模块

@author: HSS
@since: 2015-8-11
@summary: 澳洲新足迹
"""
import re
from bs4 import BeautifulSoup
from utils import *
import config
import gifextract

def login_nychinaren(sess, src):
    """ 纽约华人登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
 # Step 1: Login
    payload = {}

    #将src['username']内容，src['password']加密后内容存入payload中
    payload['username'] = src['username']
    payload['password'] = src['password']
    payload['autologin'] = 'on'
    payload['login'] = '登 录'
    payload['redirect'] = ''

    #发送post包
    resp = sess.post('http://www.nychinaren.com/f/page_login', data=payload,
                     headers={
                         'Referer':'http://www.nychinaren.com/f/page_login',
                         'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.94 Safari/537.36'
                     })
    # print_to_file(resp.content)
    #判断登录后页面是否含有用户字段，若存在则证明登录成功，否则失败
    if src['username'] in resp.content:
        return True
    return False

def post_nychinaren_forum(post_url, src):
    """纽约华人论坛主贴模块
    @author: HSS
    @since: 2015-8-11

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   板块地址  http://www.nychinaren.com/f/page_viewforum/f_19.html
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    logger = RAPLogger(post_url)
    sess = RAPSession(src)
    host = 'http://www.nychinaren.com/'
    # Step 1: 登录
    if not login_nychinaren(sess, src):
        logger.error(' Login Error')
        return ('', str(logger))
    logger.info(' Login OK')

    fid = re.findall(r'f_(\d+)', post_url)[0]
    resp = sess.get(host + '/f/page_pppping/mode_newtopic/f_'+fid+'.html')
    soup = BeautifulSoup(resp.content)

    form = soup.find('form', attrs={'id': 'post'})
    payload = get_datadic(form)
    payload['subject'] = src['subject']
    payload['message'] = '<div>'+src['content']+'</div>'
    payload['tags'] = '中国'

    #发送post包
    resp = sess.post(host + form['action'], data=payload)
    print_to_file(resp.content)
    if '成功' in resp.content:
        logger.info('Post OK')
    else:
        logger.error('Post Error')
        return ('', str(logger))
    url = host + re.findall(r'a href="(.*?)">这里</a> 阅读', resp.content)[0]
    return (url, str(logger))