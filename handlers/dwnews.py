# -*- coding: utf-8 -*- 

import re, random

import utils
import config
from bs4 import BeautifulSoup
uid = ''
def login_dwnews(sess, src):
    """ 多维社区登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    payload = {
        'format':'json',
        'callback':'?',
        'username':src['username'],
        'password':src['password'],
        'rememberMe':'0',
        'url':'http://blog.dwnews.com/'
    }
    # 发送登录get包
    resp = sess.get('http://passport.dwnews.com/ucenter/login', params=payload)
    if 'ok' not in resp.content:
        return False
    global uid
    uid = re.findall(r'"uid":"(.*?)"',resp.content)[0]
    username = re.findall(r'"username":"(.*?)"',resp.content)[0]
    password = re.findall(r'"password":"(.*?)"',resp.content)[0]
    email = re.findall(r'"email":"(.*?)"',resp.content)[0]
    payload = {
        'r':'login/checkLogin',
        'callback':'?',
        'uid':uid,
        'username':username,
        'password':password,
        'email':email,
        'rememberMe':'0',
        'url':'http://blog.dwnews.com/'
    }
    # 发送登录get包
    resp = sess.get('http://blog.dwnews.com/index.php', params=payload)
    # 若指定字样出现在response中，表示登录成功
    if 'success' not in resp.content:
        return False
    return True
# Coding: utf8
# Captcha: not required
# Login: not required
def reply_dwnews_news(post_url, src):
    s = utils.RAPSession(src)
    logger = utils.RAPLogger(post_url)

    # Step 1: 登录
    if not login_dwnews(s, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.info(' Login OK')
    r = s.get(post_url)
    ikey = re.findall('ikey = "(\w*)"', r.content)[0]

    r = s.get('http://blog.dwnews.com/index.php', params={
            'r': 'comment/post',
            'callback': 'success_jsonpCallback',
            'doitem': 'post',
            'content': src['content'],
            'type': 'news',
            'author': uid,
            'url': ikey,
            'club_id': '',
            'facebook': 0,
            'twitter': 0,
            '_': str(random.random()),
        }, headers={'Referer': post_url})

    if 'success' not in r.content:
        logger.info('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))

# Coding: utf8
# Captcha: not required
# Login: not required
def reply_dwnews_blog(post_url, src):
    s = utils.RAPSession(src)
    logger = utils.RAPLogger(post_url)

    # Step 1: 登录
    if not login_dwnews(s, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.info(' Login OK')
    r = s.get(post_url)
    ikey = re.findall('ikey = "(\w*)"', r.content)[0]
    club_id = re.findall('post-(\d*)', post_url)[0]
    r = s.get('http://blog.dwnews.com/index.php', params={
            'r': 'comment/post',
            'callback': '?',
            'doitem': 'post',
            'content': src['content'],
            'type': 'club',
            'author': uid,
            'url': ikey,
            'club_id': club_id,
            'facebook': 0,
            'twitter': 0,
        }, headers={'Referer': post_url})

    if 'success' not in r.content:
        logger.info('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))

def post_dwnews_blog(post_url, src):
    """ 多维社区发主贴函数

        - Name:     多维社区
        - Feature:  http://blog.dwnews.com/
        - Captcha:  NO
        - Login:    NO

    @param post_url:   板块地址 如：http://blog.dwnews.com/
    @type post_url:    str

    @param src:        用户名，密码，标题，主帖内容，等等。
    @type src:         dict

    @return:           是否发帖成功，帖子URL
    @rtype:            bool,str

    """
    logger = utils.RAPLogger(post_url)
    sess = utils.RAPSession(src)
    # Step 1: 登录
    if not login_dwnews(sess, src):
        logger.error(' Login Error')
        return ('', str(logger))
    logger.info(' Login OK')
    # Step 2: 验证用户，取得Token
    resp = sess.get('http://blog.dwnews.com/index.php?r=user/checkMember&callback=?')
    csrf_token = re.findall(r'"CsrfToken":"(.*?)"',resp.content)[0].replace('\\','')
    logger.info('csrf_token: ' + csrf_token)

    # 回复
    payload = {
        'title':src['subject'],
        'content':'<p>'+src['content']+'</p>',
        'tag':'时事',
        'catid':'5',
        'facebook':'0',
        'twitter':'0',
        'linkedin':'0',
        'google':'0',
        'CsrfToken':csrf_token
    }
    resp = sess.post('http://blog.dwnews.com/index.php?r=club/post', data=payload,
                     headers={
                         'Accept':'application/json, text/javascript, */*; q=0.01',
                         'Referer':'http://blog.dwnews.com/mytopic',
                         'X-Requested-With': 'XMLHttpRequest',
                     })
    # 若指定字样出现在response中，表示发帖成功
    if 'success' not in resp.content:
        logger.info(resp.content)
        logger.error(' Post Error')
        return ('', str(logger))
    resp = sess.get('http://blog.dwnews.com/index.php?r=club/makehtml&catid=5')
    if 'ok' not in resp.content:
        logger.info(resp.content)
        logger.error(' Post Error')
        return ('', str(logger))
    logger.info(' Post OK')
    resp = sess.get('http://blog.dwnews.com/mytopic')
    soup = BeautifulSoup(resp.content)
    url = soup.select('div.loadMore li a[href^="http"]')[0]['href']
    return (url, str(logger))
    