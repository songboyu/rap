# -*- coding: utf-8 -*-
"""飞月网新闻回复模块

@author: sky
@since: 2014-12-08
@summary: 飞月网新闻
"""
import re
from bs4 import BeautifulSoup
from hashlib import md5
from utils import *
import urllib
import random
import config
import gifextract
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
    login_page = 'http://bbs.onmoon.com/'
    resp = sess.get(login_page + '/member.php?mod=logging&action=login')
    #获取登录页面content的HTML
    soup = BeautifulSoup(resp.content)
    #查找与{'name': 'login'}匹配的form标签
    form = soup.find('form', attrs={'name': 'login'})
    #将form标签中的form属性内容存入payload中
    payload = get_datadic(form)

    #将src['username']内容，src['password']加密后内容存入payload中
    payload['username'] = src['username']
    payload['password'] = md5(src['password']).hexdigest()

    sechash = soup.find('input', attrs={'name': 'sechash'})['value']
    resp = sess.get('http://bbs.onmoon.com/misc.php?mod=seccode&action=update&idhash='+sechash+'&inajax=1&ajaxtarget=seccode_'+sechash)

    resp = sess.get('http://bbs.onmoon.com/'+re.findall(r'src="(.*?)"' ,resp.content)[0],
                    headers={'Accept': config.accept_image,
                             'Referer': 'http://bbs.onmoon.com/member.php?mod=logging&action=login'})
    with open('1.gif', 'wb') as f:
        f.write(resp.content)
    gif_last_frame = gifextract.processImage('1.gif')
    seccode = crack_captcha(open('gif/1.gif-9.png').read())
    print seccode
    payload['seccodeverify'] = seccode
    #发送post包
    resp = sess.post(login_page + form['action'], data=payload)
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
    # Step 1: 登录
    if not login_powerapple(sess, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.info(' Login OK')

    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)

    name = soup.find('input', attrs={'id': 'plid'})
    name1 = name.attrs['value']
    payload = {}
    payload['']=src['content']
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
    