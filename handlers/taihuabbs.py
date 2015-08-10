# -*- coding: utf-8 -*-
"""泰国华人论坛

@author: HSS
@since: 2015-8-10
@summary: 泰国华人论坛

"""
import requests, re, random, logging, time
from bs4 import BeautifulSoup

import config
from utils import *

CHARSET = 'gbk'

def login_taihuabbs(sess, src):
    """ 泰国华人论坛登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    host = 'http://www.taihuabbs.com/'
    resp = sess.get(host + '/thread-htm-fid-106.html')
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'name': 'login_FORM'})

    payload = get_datadic(form, CHARSET)
    payload['pwuser'] = src['username'].decode('utf8').encode(CHARSET)
    payload['pwpwd'] = src['password'].decode('utf8').encode(CHARSET)
    # 发送登录post包
    resp = sess.post(host + form['action'], data=payload)

    # 若指定字样出现在response中，表示登录成功
    if u'success' not in resp.content.decode(CHARSET):
        return False
    return True

def post_taihuabbs_forum(post_url, src):
    """泰国华人论坛发主贴模块

    @author: HSS
    @since: 2015-1-24

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   板块地址 http://www.taihuabbs.com/thread-htm-fid-106.html
    @type post_url:    str

    @param src:        用户名，密码，标题，帖子内容等等。
    @type src:         dict

    @return:           是否发帖成功
    @rtype:            bool

    """
    host = 'http://www.taihuabbs.com/'
    logger = RAPLogger(post_url)
    sess = RAPSession(src)
    # Step 1: 登录
    if not login_taihuabbs(sess, src):
        logger.error(' Login Error')
        return ('', str(logger))
    logger.info(' Login OK')

    fid = re.findall(r'fid-(\d*)', post_url)[0]
    resp = sess.get(host + '/post.php?fid='+fid)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id': 'mainForm'})
    try:
        payload = get_datadic(form)
    except:
        logger.error('Post Error:用户组每日限制发帖5篇')
        return ('', str(logger))
    payload['atc_title'] = src['subject'].decode('utf8').encode(CHARSET)
    payload['atc_content'] = '<div>'+src['content'].decode('utf8').encode(CHARSET)+'</div>'
    payload['p_type'] = '38'
    payload['p_sub_type'] = '0'
    payload['atc_credittype'] = 'money'
    payload['atc_enhidetype'] = 'money'
    payload['replyrewardcredit'] = 'money'
    payload['replyreward[replyrewardreptimes]'] = '1'
    payload['replyreward[replyrewardchance]'] = '10'
    payload['qkey'] = '-1'
    # a, o, b = re.findall(ur'验证问题:.*?(\d+)(.*?)(\d+)', resp.content.decode(CHARSET))[0]
    # # print m
    # # a = m[0], o = m[1], b = m[2]
    # if u'+' in o:
    #     r = int(a) + int(b)
    # else:
    #     r = int(a) - int(b)
    # payload['qanswer'] = r
    #
    # print a,o,b,'= '+str(r)

    # captcha_url = re.findall(r'cloudcaptchaurl = "(.*?)"', resp.content)[0]
    # resp = sess.get(captcha_url,
    #                 headers={'Accept': config.accept_image,
    #                          'Referer': host + '/post.php?fid='+fid})
    # seccode = crack_captcha(resp.content)
    # payload['gdcode'] = seccode
    print payload
    time.sleep(3)
    resp = sess.post(host + form['action'], data=payload)
    print resp.content.decode(CHARSET)

    if u'success' not in resp.content.decode(CHARSET):
        logger.error('Post Error')
        return ('', str(logger))
    logger.info('Post OK')
    return (host+re.findall(r'\[success	(.*?)\]', resp.content)[0], str(logger))