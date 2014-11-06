# -*- coding: utf-8 -*-
"""香港独立媒体模块

@author: HSS
@since: 2014-10-20
@summary: 香港独立媒体

@var CHARSET: 香港独立媒体网页编码
@type CHARSET: str

"""
import re

from bs4 import BeautifulSoup

import utils

CHARSET = 'utf8'
HOST = 'https://www.facebook.com'

def login_inmediahk(sess, src):
    """ 香港独立媒体登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    payload = {
        'external_page_url':src['external_page_url'],
        'iframe_src':src['iframe_src'],
        'locale':'zh_HK',
        'display':'popup',
        'social_plugin':'multi_login',
        'cancel_url':'https://www.facebook.com/connect/window_comm.php?_id=fcecdd1f4&_relation=opener',
        'next':'https://www.facebook.com/plugins/multi_login_popup_loggedin.php',
        'provider':'facebook'
    }
    resp = sess.get('https://www.facebook.com/login.php', params=payload)
    soup = BeautifulSoup(resp.content)
    # 获得登录form
    form = soup.find('form', attrs={'id': 'login_form'})

    payload = utils.get_datadic(form)
    payload['email'] = src['username']
    payload['pass'] = src['password']
    # 发送登录post包
    resp = sess.post(HOST+form['action'], data=payload,
                     headers={
                         'Origin':'https://www.facebook.com',
                         'Referer':resp.url,
                         'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                      'Chrome/37.0.2062.124 Safari/537.36',
                         'X-DevTools-Emulate-Network-Conditions-Client-Id':'97765AD6-3270-4C0F-A8B0-6267258612E0'
                     })
    # 若指定字样出现在response中，表示登录成功
    print resp.content
    if 'Redirecting' in resp.content:
        return False
    return True


def reply_inmediahk(post_url, src):
    """ 香港独立媒体回复函数

        - Name:     香港独立媒体
        - Feature:  www.inmediahk.net
        - Captcha:  NO
        - Login:    YES

    @param post_url:   帖子地址
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict
    
    @return:           是否回复成功
    @rtype:            bool

    """
    logger = utils.RAPLogger(post_url)
    sess = utils.RAPSession(src)

    faild_info = {'Error':'Failed to get account info'}
    payload = {
        'api_key':'408250695928069',
        'channel_url':'http://static.ak.facebook.com/connect/xd_arbiter/QjK2hWv6uak.js?version=41#cb=f552c5c88&domain='
                      'www.inmediahk.net&origin=http%3A%2F%2Fwww.inmediahk.net%2Ffee0db6f8&relation=parent.parent',
        'colorscheme':'light',
        'href':post_url,
        'locale':'zh_HK',
        'numposts':50,
        'sdk':'joey',
        'skin':'light',
        'width':589
    }
    resp = sess.get(HOST+'/plugins/feedback.php', params=payload)
    # Step 1: 登录
    src['external_page_url'] = post_url
    src['iframe_src'] = resp.url

    if not login_inmediahk(sess, src):
        logger.error(' Login Error')
        return (faild_info, str(logger))
    logger.info(' Login OK')
    resp = sess.get(HOST+'/plugins/feedback.php', params=payload)
    # 回复
    soup = BeautifulSoup(resp.content)
    # 获得回复form
    form = soup.find('form', attrs={'rel': 'async'})
    payload = utils.get_datadic(form)
    payload['text_text'] = src['content']
    payload['text'] = src['content']
    # payload['post_to_profile'] = 'on'
    payload['__user'] = payload['commentas']
    payload['__rev'] = re.findall(r'{\"revision\":(.*?),',resp.content)[0]
    payload['__a'] = '1'
    payload['__req'] = '1'
    payload['__dyn'] = '7wci2e4oK4pomXWo2vwAxu6E'
    payload['ttstamp'] = '265816910453508648110120112113'
    # payload['iframe_referer'] = resp.url
    print payload
    # 发送登录post包
    resp = sess.post(HOST+form['action'], data=payload,
                     headers={
                         'host':'www.facebook.com',
                         'method':'POST',
                         'path':'/ajax/connect/feedback.php',
                         'scheme':'https',
                         'version':'HTTP/1.1',
                         'accept':'*/*',
                         'origin':HOST,
                         'referer':resp.url,
                         'user-agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                      'Chrome/37.0.2062.124 Safari/537.36',
                     })
    # print resp.headers
    # print resp.request.headers
    print resp.content
    if 'payload' not in resp.content:
        logger.error(' Reply Error')
        return (False, str(logger))
    logger.info(' Reply OK')
    return (True, str(logger))
