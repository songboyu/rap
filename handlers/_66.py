# -*- coding: utf-8 -*-
"""66网模块

@author: HSS
@since: 2015-8-10
@summary: 66网

@var CHARSET: 66网网页编码
@type CHARSET: str

"""
import re
from bs4 import BeautifulSoup
import time
from utils import *
# Coding: utf8
# Captcha: not required
# Login: required

CHARSET = 'gbk'

def login_66_forum(sess, src):
    """66网论坛登录模块

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    host = 'http://www.66.ca/'

    resp = sess.get(host + 'member.php?mod=logging&action=login')
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'name': 'login'})
    payload = get_datadic(form)
    payload['loginfield'] = 'username'
    payload['username'] = src['username']
    payload['password'] = src['password']
    payload['questionid'] = 0
    payload['answer'] = ''
    resp = sess.post(host + form['action'] + '&inajax=1', data=payload)
    # 若指定字样出现在response中，表示登录成功
    if 'succeedmessage' not in resp.content:
        return False
    return True

# Coding: utf8
# Captcha: not required
# Login: required
def post_66_forum(post_url, src):
    """66网论坛发主贴模块

    @author: sky
    @since: 2014-12-01

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   帖子地址  http://www.66.ca/forum.php?mod=forumdisplay&fid=36
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    logger = RAPLogger(post_url)
    sess = RAPSession(src)

    # 登录
    if not login_66_forum(sess, src):
        logger.error('Login Error')
        return ('', str(logger))
    logger.info('Login OK')

    fid = re.findall(r'fid=(\d+)', post_url)[0]
    resp = sess.get('http://www.66.ca/forum.php?mod=post&action=newthread&fid='+fid)
    soup = BeautifulSoup(resp.content)
    # 获得发帖form表单
    form = soup.find('form', attrs={'id': 'postform'})

    # 构造回复参数
    payload = get_datadic(form)
    payload['posttime'] = int(time.time()*1000)
    payload['wysiwyg'] = '1'
    payload['subject'] = src['subject'].decode('utf8').encode(CHARSET)
    payload['message'] = src['content'].decode('utf8').encode(CHARSET)

    #发送发主贴post包
    resp = sess.post('http://www.66.ca/'+form['action'], data=payload)
    # 若指定字样出现在response中，表示发帖成功
    if src['subject'] not in resp.content:
        logger.error('Post Error')
        return ('', str(logger))
    logger.info('Post OK')
    return (resp.url, str(logger))
