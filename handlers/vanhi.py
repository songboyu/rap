# -*- coding: utf-8 -*- 
"""温哥华巅峰

@author: sniper
@since: 2015-1-16
@summary: 温哥华巅峰
"""

import re
import urllib
import time
import binascii

from bs4 import BeautifulSoup

from utils import *

CHARSET = 'gbk'

def login_vanhi(sess, src):
    # Load login page.
    host = 'http://forum.vanhi.com/'
    resp = sess.get(host + 'member.php?mod=logging&action=login&referer=&infloat=yes&handlekey=login&inajax=1&ajaxtarget=fwin_content_login', 
                    headers={'Referer': 'http://forum.vanhi.com/'})
    payload = {
        'username': src['username'],
        'password': src['password'],
        'formhash': re.findall('name="formhash" value="(\w+)"', resp.content)[0],
        'referer': 'http://forum.vanhi.com/',
        'loginfield': 'username',
        'questionid': 0,
        'answer': '',
        'loginsubmit': 'true',
    }
    payload['username'] = src['username']
    payload['password'] = src['password']

    url = host + re.findall('action="([^>]+?)"', resp.content)[0] + '&inajax=1'
    url = url.replace('&amp;', '&')
    resp = sess.post(url, data=payload)
    with open('1.html', 'w') as f:
        f.write(resp.content)
    if u'欢迎'.encode(CHARSET) not in resp.content:
        return False
    return True


def reply_vanhi_forum(post_url, src):
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    sess = RAPSession(src)

    # Login
    if not login_vanhi(sess, src):
        logger.error('Login Error')
        return (False, str(logger))
    logger.info('Login OK')

    # Reply
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'fastpostform'})
    payload = get_datadic(form, CHARSET)
    payload['message'] = src['content'].decode('utf8').encode(CHARSET)

    resp = sess.post(host + form['action'] + '&inajax=1', data=payload)
    if u'成功'.encode(CHARSET) not in resp.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))


def post_vanhi_forum(post_url, src):
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    sess = RAPSession(src)

    # Login
    if not login_vanhi(sess, src):
        logger.error('Login Error')
        return ('', str(logger))
    logger.info('Login OK')

    # Post
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'fastpostform'})
    payload = get_datadic(form, CHARSET)
    payload['subject'] = src['subject'].decode('utf8').encode(CHARSET,'ignore')
    payload['message'] = src['content'].decode('utf8').encode(CHARSET,'ignore')

    resp = sess.post(host + form['action'] + '&inajax=1', data=payload)
    if u'主题已发布'.encode(CHARSET) not in resp.content:
        logger.error('Post Error')
        return ('', str(logger))
    logger.info('Post OK')
    url = 'http://forum.vanhi.com/forum.php?mod=viewthread&tid=' + re.findall("'tid':'(\d+)'", resp.content)[0]
    return (url, str(logger))


def get_account_info_vanhi_forum(src):
    """ 温哥华巅峰账户信息获取函数

    @param src:        用户名，密码
    @type src:         dict

    @return:           账户信息
    @rtype:            dict
    """
    logger = RAPLogger(src['username'])
    sess = RAPSession(src)

    # Step 1: 登录
    if not login_vanhi(sess, src):
        logger.error(' Login Error')
        return ({}, str(logger))
    logger.info(' Login OK')

    resp = sess.get('http://forum.vanhi.com/home.php?mod=space&do=profile')
    
    html = resp.content.decode(CHARSET).encode('utf8')

    head_image = re.findall(r'img src="(.*avatar.*)"', html)[0]

    account_score = re.findall(r'<li><em>积分</em>(.*?)</li>', html)[0]
    account_class = re.findall(r'ac=usergroup.*>(.*?)</a>', html)[0]

    time_register = re.findall(r'<li><em>注册时间</em>(.*?)</li>', html)[0]
    time_last_login = re.findall(r'<li><em>上次活动时间</em>(.*?)</li>', html)[0]

    login_count = ''

    count_post = re.findall(r'主题数 (.*?)<', html)[0]
    count_reply = re.findall(r'回帖数 (.*?)<', html)[0]

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

def upload_head_vanhi_forum(src):
    logger = RAPLogger('Upload head vanhi_forum=>' + src['username'])
    sess = RAPSession(src)

    # Step 1: 登录
    if not login_vanhi(sess, src):
        logger.error('Login Error')
        return ('', str(logger))
    logger.info('Login OK')

    resp = sess.get('http://http://forum.vanhi.com/home.php?mod=spacecp&ac=avatar')
    input = urllib.unquote(re.findall(r'input=(.*?)&',resp.content)[0])
    agent = re.findall(r'agent=(.*?)&',resp.content)[0]
    head_url = re.findall(r'<td><img src="(.*?)"',resp.content)[0]
    print 'input:',input
    print 'agent:',agent

    avatar1 = binascii.hexlify(open(src['head'],'rb').read()).upper()
    avatar2 = avatar1
    avatar3 = avatar1

    params = {
        'm':'user',
        'inajax':'1',
        'a':'rectavatar',
        'appid':'1',
        'input':input,
        'agent':agent,
        'avatartype':'virtual'
    }
    payload = {
        'avatar1':avatar1,
        'avatar2':avatar2,
        'avatar3':avatar3,
        'urlReaderTS':str(time.time()*1000)
    }
    resp = sess.post('http://http://forum.vanhi.com/uc_server/index.php', data=payload, params=params)


    print resp.content
    if 'success="1"' in resp.content:
        logger.info('uploadavatar OK')
        return (head_url, str(logger))
    else:
        logger.info('uploadavatar Error')
        return ('', str(logger))
