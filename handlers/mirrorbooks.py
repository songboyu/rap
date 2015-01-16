# -*- coding: utf-8 -*-
"""明镜新闻网模块

@author: HSS
@since: 2014-11-30
@summary: 明镜新闻网

"""
import requests, re, random, logging
from bs4 import BeautifulSoup

import config
from utils import *
def login_mirrorbooks(sess, src):
    """ 明镜新闻网登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    if src['TTL'] == 0:
        return False
    login_url = 'http://www.mirrorbooks.com/MIB/member/login.aspx'
    resp = sess.get(login_url)
    # 构造回复参数
    payload = {
        'tbx_Admin': src['username'],
        'tbx_pwd':src['password'],
        'rbl_CookiesDate': '1',
        '__VIEWSTATE': re.findall('id="__VIEWSTATE" value="(.*?)"', resp.content)[0],
        '__EVENTVALIDATION': re.findall('id="__EVENTVALIDATION" value="(.*?)"', resp.content)[0],
        '__EVENTTARGET':'',
        'btn_ok': '登入',
    }
    resp = sess.get('http://www.mirrorbooks.com/MIB/UserControls/imgcode.aspx',
        headers={
            'Accept': config.accept_image,
            'Referer': login_url,
        })
    seccode = crack_captcha(resp.content)
    payload['ImageCode$tbx_Code'] = seccode
    # 发送登录post包
    resp = sess.post(login_url, data=payload)
    # 若指定字样出现在response中，表示登录成功
    if src['username']+'您好' not in resp.content:
        src['TTL'] -= 1
        return login_mirrorbooks(sess, src)
    return True

# Coding: utf8
# Captcha: required
# Login: not required
def reply_mirrorbooks_news(post_url, src):
    if src['TTL'] == 0:
        raise RAPMaxTryException('captcha')
    logger = RAPLogger(post_url)

    # This handler works for 'www.mirrorbooks.com' and 'www.mingjingnews.com'
    # 'mingjingnews' is a synonym for 'mirrorbooks', but the reply is always unsuccessful(Captcha error while I don't know why).
    # So I just redirect 'mingjingnews' to 'mirrorbooks' if necessary.
    if 'mingjingnews' in post_url:
        post_url = post_url.replace('mingjingnews', 'mirrorbooks')

    sess = RAPSession(src)

    # Step 1: 登录
    if not login_mirrorbooks(sess, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.info(' Login OK')

    resp = sess.get(post_url)
    payload = {
        'ScriptManager1': 'UpdatePanel2|btn_reply_send',
        'NSSrc$src': 'rbl1',
        '__VIEWSTATE': re.findall('id="__VIEWSTATE" value="(.*?)"', resp.content)[0],
        '__EVENTVALIDATION': re.findall('id="__EVENTVALIDATION" value="(.*?)"', resp.content)[0],
        '__ASYNCPOST': 'true',
        'btn_reply_send': '發表',
        'tbx_CKEditor': src['content'],
    }

    resp = sess.get('http://www.mirrorbooks.com/MIB/UserControls/imgcode.aspx',
        headers={
            'Accept': config.accept_image,
            'Referer': post_url,
        })
    seccode = crack_captcha(resp.content)
    payload['ImageCode$tbx_Code'] = seccode
    resp = sess.post(post_url, data=payload)
    if '發表成功' not in resp.content:
        logger.error('Reply Error')
        if '驗証碼' in resp.content:
            src['TTL'] -= 1
            return reply_mirrorbooks_news(post_url, src)
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))

def post_mirrorbooks_blog(post_url, src):
    """ 明镜新闻网博客发主贴函数

    @param post_url:   板块地址 如：http://www.mirrorbooks.com/MIB/blog/main.aspx
    @type post_url:    str

    @param src:        用户名，密码，标题，主帖内容，等等。
    @type src:         dict

    @return:           是否发帖成功，帖子URL
    @rtype:            bool,str

    """
    if src['TTL'] == 0:
        raise RAPMaxTryException('captcha')
    logger = RAPLogger(post_url)
    sess = RAPSession(src)

    # Step 1: 登录
    if not login_mirrorbooks(sess, src):
        logger.error(' Login Error')
        return (False, '', str(logger))
    logger.info(' Login OK')

    post_new_url = 'http://www.mirrorbooks.com/MIB/blog/manager_add.aspx'
    resp = sess.get(post_new_url)
    payload = {
        'ScriptManager1': 'UpdatePanel3|ibtn_Add',
        'BGSrc$src': 'rbl1',
        '__EVENTTARGET':'',
        '__EVENTARGUMENT':'',
        '__VIEWSTATE': re.findall('id="__VIEWSTATE" value="(.*?)"', resp.content)[0],
        '__EVENTVALIDATION': re.findall('id="__EVENTVALIDATION" value="(.*?)"', resp.content)[0],
        'BGSrc$tbx_Src':'',
        'ddl_BlogType':'01',
        'ddl_PrivateType':'',
        'tbx_Title':src['subject'],
        'rbl_Public':'1',
        'tbx_KeyWord':'',
        'tbx_CKEditor':src['content'],
        '__ASYNCPOST': 'true',
        'ibtn_Add.x':'78',
        'ibtn_Add.y':'6'
    }

    resp = sess.get('http://www.mirrorbooks.com/MIB/UserControls/imgcode.aspx',
        headers={
            'Accept': config.accept_image,
            'Referer': post_new_url,
        })
    seccode = crack_captcha(resp.content)
    payload['ImageCode$tbx_Code'] = seccode.encode('utf8')

    resp = sess.post(post_new_url, data=payload)
    if 'updatePanel' not in resp.content:
        logger.error('Post Error')
        return (False, '', str(logger))
    logger.info('Post OK')
    resp = sess.get('http://www.mirrorbooks.com/MIB/blog/manager.aspx')
    href = re.findall(r'<a href=\'(.*?)\' target="_blank" > ' + src['subject'] + '</a>', resp.content)[0]
    url = 'http://www.mirrorbooks.com/MIB/blog/'+href
    print url
    return (True, url, str(logger))