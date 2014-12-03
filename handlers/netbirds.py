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

from bs4 import BeautifulSoup

import utils

CHARSET = 'utf-8'

# Coding: utf8
# Captcha: arithmetic
# Login: required
def login_netbirds(sess, src):
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
    login_page = 'http://www.netbirds.com/'
    resp = sess.get(
        login_page + '/do/hack.php?hack=login&iframeID=head_loginer&styletype=yellow')
    #获取登录页面content的HTML
    soup = BeautifulSoup(resp.content)
    #查找与{'name': 'login'}匹配的form标签
    form = soup.find('form', attrs={'class': 'login_form'})
    #将form标签中的form属性内容存入payload中
    payload = utils.get_datadic(form)

    #将src['username']内容，src['password']加密后内容存入payload中
    payload['username'] = src['username']
    payload['password'] = md5(src['password']).hexdigest()

    #发送post包
    resp = sess.post(login_page + form['action'], data=payload)
    soup = BeautifulSoup(resp.content)

    #判断登录后页面是否含有用户字段，若存在则证明登录成功，否则失败
    if  u'安全退出' in resp.content:
        return True
    return False

def post_netbirds_forum(post_url, src):

     # Returnable logger
    logger = utils.RAPLogger(post_url)
    host = utils.get_host(post_url)
    sess = utils.RAPSession(src)

    # Step 1: 登录
    if not login_netbirds(sess, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.info(' Login OK')

    resp = sess.get('http://www.backchina.com/forum.php?mod=post&action=newthread&fid=37')
    soup = BeautifulSoup(resp.content)
    # 获得发帖form
    form = soup.find('form', attrs={'id': 'postform'})
    # 构造回复参数
    payload = utils.get_datadic(form)
    payload['subject'] = src['subject'].decode('utf8').encode(CHARSET)
    payload['message'] = src['content'].decode('utf8').encode(CHARSET)
    #payload['font1'] = u'[原创]'.encode(CHARSET)
    # 发送发帖post包
    resp = sess.post('http://www.backchina.com/forum.php?mod=post&action=newthread&fid=37&extra=&topicsubmit=yes', data=payload)

    # print resp.content.decode(CHARSET)
    # 若指定字样出现在response中，表示发帖成功
    if src['content'] not in resp.content:
        logger.error(' Post Error')
        return (False, '', str(logger))
    logger.info(' Post OK')
    url = re.findall(r'<link rel="canonical" href="(.*?)" />',resp.content)[0]
    print url
    logger.info(url)
    return (True, url, str(logger))

