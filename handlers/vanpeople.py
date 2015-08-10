# -*- coding: utf-8 -*-
"""人在温哥华模块

@author: sky
@since: 2014-12-08
@summary: 人在温哥华
"""
import re
from bs4 import BeautifulSoup
from utils import *
import urllib
import random
import config

def login_vanpeople(sess, src):
    """ 人在温哥华登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """

 # Step 1: Login
    #登录页面
    login_page = 'http://forum.vanpeople.com/'
    resp = sess.get(login_page + '/member.php?mod=logging&action=login')
    #获取登录页面content的HTML
    soup = BeautifulSoup(resp.content)
    #查找与{'name': 'login'}匹配的form标签
    form = soup.find('form', attrs={'name': 'login'})
    #将form标签中的form属性内容存入payload中
    payload = get_datadic(form)

    #将src['username']内容，src['password']加密后内容存入payload中
    payload['username'] = src['username']
    payload['password'] = src['password']
    payload['questionid'] = 0
    payload['loginfield'] = 'username'

    sechash = soup.find('input', attrs={'name': 'sechash'})['value']
    resp = sess.get('http://forum.vanpeople.com/misc.php?mod=seccode&action=update&idhash='+sechash+'&inajax=1&ajaxtarget=seccode_'+sechash)

    resp = sess.get('http://forum.vanpeople.com/'+re.findall(r'src="(.*?)"', resp.content)[0],
                    headers={'Accept': config.accept_image,
                             'Referer': 'http://forum.vanpeople.com/member.php?mod=logging&action=login'})
    seccode = crack_captcha(resp.content)
    print seccode
    payload['seccodeverify'] = seccode

    #发送post包
    resp = sess.post(login_page + form['action']+'&inajax=1', data=payload)
    with open('attach/result.png', 'wb') as f:
        f.write(resp.content)
    print payload
    #判断登录后页面是否含有用户字段，若存在则证明登录成功，否则失败
    if src['username'] in resp.content:
        return True
    return False

def post_vanpeople_forum(post_url, src):
    """人在温哥华主贴模块
    @author: sky
    @since: 2014-12-08

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   板块地址  http://forum.vanpeople.com/forum.php?mod=forumdisplay&fid=67
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    sess = RAPSession(src)
    # Step 1: 登录
    if not login_vanpeople(sess, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.info(' Login OK')

    fid = re.findall(r'fid=(\d+)', post_url)[0]
    resp = sess.get('http://forum.vanpeople.com/forum.php?mod=post&action=newthread&fid='+fid)
    soup = BeautifulSoup(resp.content)

    form = soup.find('form', attrs={'id': 'postform'})
    payload = get_datadic(form)
    payload['subject'] = src['subject']
    payload['message'] = src['content']

    #发送post包
    resp = sess.post('http://forum.vanpeople.com/' + form['action'], data=payload)

    with open('attach/1.html', 'w') as f:
        f.write(resp.content)

    if src['content'] in resp.content:
        logger.info('Post OK')
    else:
        logger.error('Post Error')
        return ('', str(logger))
    return (resp.url, str(logger))

