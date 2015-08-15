# -*- coding: utf-8 -*-
"""飞月网模块

@author: HSS
@since: 2015-8-10
@summary: 飞月网
"""
import re
from bs4 import BeautifulSoup
from utils import *
import urllib
import random
import config
import gifextract

def login_onmoon(sess, src):
    """ 飞月网登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
 # Step 1: Login
    #登录页面
    host = 'http://bbs.onmoon.com/'
    resp = sess.get(host + '/member.php?mod=logging&action=login')
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
    resp = sess.get(host + '/misc.php?mod=seccode&action=update&idhash='+sechash+'&inajax=1&ajaxtarget=seccode_'+sechash)

    resp = sess.get(host + re.findall(r'src="(.*?)"', resp.content)[0],
                    headers={'Accept': config.accept_image,
                             'Referer': host + '/member.php?mod=logging&action=login'})
    result = gifextract.processImage(resp.content, 'attach/result.png')
    seccode = crack_captcha(result)
    print seccode
    payload['seccodeverify'] = seccode

    #发送post包
    resp = sess.post(host + form['action']+'&inajax=1', data=payload)
    # with open('attach/1.html', 'w') as f:
    #     f.write(resp.content)
    print payload
    #判断登录后页面是否含有用户字段，若存在则证明登录成功，否则失败
    if src['username'] in resp.content:
        return True
    return False

# Coding: utf8
# Captcha: not required
# Login: not required
def reply_onmoon_news(post_url, src):
    """飞月网新闻回复模块
    @author: sky
    @since: 2014-12-08

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   帖子地址  http://www.onmoon.com/chs/2014/11/30/800307.html
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    logger = RAPLogger(post_url)

    host = get_host(post_url)
    sess = RAPSession(src)

    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)

    name = soup.find('input', attrs={'id': 'plid'})
    name1 = name.attrs['value']
    payload = {}
    payload[''] = src['content']
    u = urllib.urlencode(payload)
    resp = sess.get(host + 'pl.php?nid=' + name1 + '&pl=' + u[1:]+ '&randomnumber=' + str(random.randint(1000,9999)))
    
    #再次请求原网页，查看是否已经有回帖内容
    resp = sess.get(post_url)

    #with open('1.html', 'w') as f:
    #    f.write(resp.content)
    #判断回帖后页面是否含有回帖内容，若存在则证明回帖成功，否则失败
    if src['content'] in resp.content:
        logger.info('Reply OK')
    else:
        logger.error('Reply Error')
        return (False, str(logger))
    return (True, str(logger))

def post_onmoon_forum(post_url, src):
    """飞月网论坛主贴模块
    @author: HSS
    @since: 2015-8-10

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   板块地址  http://bbs.onmoon.com/forum.php?mod=forumdisplay&fid=48
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    logger = RAPLogger(post_url)
    sess = RAPSession(src)
    host = 'http://bbs.onmoon.com/'
    # Step 1: 登录
    if not login_onmoon(sess, src):
        logger.error(' Login Error')
        return ('', str(logger))
    logger.info(' Login OK')

    fid = re.findall(r'fid=(\d+)', post_url)[0]
    resp = sess.get(host + '/forum.php?mod=post&action=newthread&fid='+fid)
    soup = BeautifulSoup(resp.content)

    form = soup.find('form', attrs={'id': 'postform'})
    payload = get_datadic(form)
    payload['subject'] = src['subject']
    payload['message'] = src['content']
    sechash = soup.find('input', attrs={'name': 'sechash'})['value']
    resp = sess.get(host + '/misc.php?mod=seccode&action=update&idhash='+sechash+'&inajax=1&ajaxtarget=seccode_'+sechash)

    resp = sess.get(host + re.findall(r'src="(.*?)"', resp.content)[0],
                    headers={'Accept': config.accept_image,
                             'Referer': host + '/forum.php?mod=post&action=newthread&fid='+fid})
    result = gifextract.processImage(resp.content, 'attach/result.png')
    seccode = crack_captcha(result)
    print seccode
    payload['seccodeverify'] = seccode

    #发送post包
    resp = sess.post(host + form['action'], data=payload)

    # if src['subject'] in resp.content:
    #     logger.info('Post OK')
    # else:
    logger.info('Post OK')
    return (resp.url, str(logger))

