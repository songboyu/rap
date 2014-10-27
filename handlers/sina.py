# -*- coding: utf-8 -*-
"""新浪回复模块

@author: HSS
@since: 2014-10-20
@summary: 新浪论坛、新浪新闻

@var CHARSET: 新浪网页编码
@type CHARSET: String

"""
import re

from bs4 import BeautifulSoup

import config
import utils

CHARSET = 'gbk'


def login_sina(session, post_url, src):
    """ 新浪登录函数

    @param session:    request.Session()
    @type session:     Session

    @param post_url:   帖子地址
    @type post_url:    String

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dictionary

    @return:           是否登录成功
    @rtype:            boolean

    """
    logger = utils.RAPLogger(post_url)
    request = session.get('http://club.mil.news.sina.com.cn/')
    soup = BeautifulSoup(request.content)
    # 获取登录form
    form = soup.find('form', attrs={'name': 'login'})
    # 构造登录函数
    payload = utils.get_datadic(form)
    payload['username'] = src['username']
    payload['password'] = src['password']
    # 登录地址
    login_url = 'https://login.sina.com.cn/sso/login.php'
    # 发送登录post包
    request = session.post(login_url, data=payload)

    post_times = 0
    # 验证是否成功，如果失败再次发送
    # 失败可能原因：验证码错误
    while u'正在登录' not in request.content.decode(CHARSET) \
            and post_times < src['TTl']:
        # 限制最大发送次数
        post_times = post_times + 1
        # 获取页面跳转地址
        redirects = re.findall(r'location.replace\(\"(.*?)\"\)',
                               request.content)
        logger.debug(' login need captcha')
        request = session.post(redirects[0])
        # 获取页面跳转地址
        redirects = re.findall(r'href=\"(.*?)\">如果',
                               request.content
                               .decode(CHARSET).encode('utf-8'))
        request = session.post(redirects[0])
        # 验证码地址
        captcha_url = re.findall(r'id=\"capcha\" src=\"(.*?)\"',
                                 request.content)[0]
        # 获取验证码图片
        captcha = session.get(captcha_url,
                              headers={
                                  'Accept': config.accept_image,
                                  'Referer': post_url
                              })
        # 获取验证码字符串
        seccode = utils.crack_captcha(captcha.content)
        logger.debug(' seccode:' + seccode)

        soup = BeautifulSoup(request.content)
        # 获取登录form
        form = soup.find('form', attrs={'name': 'login'})
        # 构造登录参数
        payload = utils.get_datadic(form)
        payload['username'] = src['username']
        payload['password'] = src['password']
        # 验证码
        payload['door'] = seccode
        # 发送登录post包
        request = session.post(login_url, data=payload)
        # 获取页面跳转地址
        redirects = re.findall(r'location.replace\(\"(.*?)\"\)',
                               request.content)
        # 获取登录结果
        request = session.post(redirects[0])
    # 若指定字样出现在response中，表示登录成功
    if u'正在登录' not in request.content.decode(CHARSET):
        message = re.findall(r'<p>(.*?)</p>', request.content)[0]
        logger.debug(message.decode(CHARSET).encode('utf-8'))
        return False
    return True


def reply_sina_club(post_url, src):
    """ 新浪论坛回复函数

        - Name:     新浪论坛
        - Feature:  (forum|club).*.sina.com.cn
        - Captcha:  YES
        - Login:    YES

    @param post_url:   帖子地址
    @type post_url:    String

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dictionary
    
    @return:           是否回复成功
    @rtype:            boolean

    """
    logger = utils.RAPLogger(post_url)
    session = utils.RAPSession(src)

    # Step 1: 登录
    if not login_sina(session, post_url, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.debug(' Login OK')

    # Step 2: 回复
    request = session.get(post_url)
    host = utils.get_host(post_url)
    # 获取回复地址
    reply_url = re.findall(r'id=\"postform\" action=\"(.*?)\"',
                           request.content)[0]
    soup = BeautifulSoup(request.content)
    # 获取回复form
    form = soup.find('form', attrs={'id': 'postform'})
    # 构造回复参数
    payload = utils.get_datadic(form)
    payload['message'] = src['content'].decode('utf8').encode(CHARSET)
    # 替换回复地址中的特殊符号
    reply_url = reply_url.replace('&amp;', '&')
    # 发送回复post包
    request = session.post(reply_url, data=payload,
                           headers={
                               'Origin': utils.get_host(post_url),
                               'Referer': post_url
                           })
    post_times = 0
    # 验证是否成功，如果失败再次发送
    # 失败可能原因：验证码错误
    while 'postform' not in request.content \
            and post_times < src['TTl']:
        # 限制最大发送次数
        post_times = post_times + 1
        logger.debug(' reply need captcha')
        # 获取验证码图片
        captcha = session.get(host + 'seccode.php',
                              headers={
                                  'Accept': config.accept_image,
                                  'Referer': reply_url
                              })
        # 获取验证码字符串
        seccode = utils.crack_captcha(captcha.content)
        logger.debug(' seccode:' + seccode)
        # 回复参数中增加验证码
        payload['seccodeverify'] = seccode.decode(CHARSET)
        # 发送回复post包
        request = session.post(reply_url, data=payload,
                               headers={
                                   'Origin': utils.get_host(post_url),
                                   'Referer': post_url
                               })
    # 若指定字样出现在response中，表示回复成功
    if 'postform' not in request.content:
        logger.error(' Reply Error')
        return (False, str(logger))
    logger.debug(' Reply OK')
    return (True, str(logger))


def reply_sina_news(post_url, src):
    """ 新浪新闻回复函数

        - Name:     新浪新闻
        - Feature:  ^http://[^(c|f)].*.sina.com.cn
        - Captcha:  YES
        - Login:    YES

    @param post_url:   新浪地址
    @type post_url:    String

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dictionary
    
    @return:           是否回复成功
    @rtype:            boolean

    """
    logger = utils.RAPLogger(post_url)
    session = utils.RAPSession(src)
    request = session.get(post_url)

    # Step 1: 登录
    if not login_sina(session, post_url, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.debug(' Login OK')

    # Step 2: 回复
    # 频道id
    channel = re.findall(r'channel:\'(.*?)\'', request.content)[0]
    # 新闻id
    newsid = re.findall(r'newsid:\'(.*?)\'', request.content)[0]

    # 构造回复参数
    payload = {
        'channel': channel,
        'newsid': newsid,
        'parent': 'B',
        'content': src['content'].decode('utf-8').encode(CHARSET),
        'format': 'js',
        'ie': CHARSET,
        'oe': CHARSET,
        'ispost': 0,
        'share_url': post_url,
        'video_url': '',
        'img_url': ''
    }
    # 回复地址
    reply_url = 'http://comment5.news.sina.com.cn/cmnt/submit'
    # 发送回复post包
    request = session.post(reply_url, data=payload,
                           headers={
                               'Referer': post_url
                           })
    # 若指定字样出现在response中，表示回复成功
    if 'result' not in request.content:
        logger.error(' Reply Error')
        return (False, str(logger))
    logger.debug(' Reply OK')
    return (True, str(logger))
