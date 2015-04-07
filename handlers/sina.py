# -*- coding: utf-8 -*-
"""新浪回复模块（新浪论坛、新浪新闻）

@author: SONG
@since: 2014-10-20
@summary: 新浪论坛、新浪新闻

@var CHARSET: 新浪网页编码
@type CHARSET: str

"""
import base64
import re
import urllib
import json
import binascii

import rsa
from bs4 import BeautifulSoup

import config
import utils

CHARSET = 'gbk'


def login_sina(sess,src):
    """ 新浪登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   帖子地址
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    url_prelogin = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.18)&_=1422354483642'
    url_login = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'

    # 获取prelogin中各项参数：servertime, nonce, pubkey, rsakv, pcid
    resp = sess.get(url_prelogin)
    json_data  = re.findall(r'\((.*?)\)', resp.content)[0]

    data       = json.loads(json_data)
    servertime = data['servertime']
    nonce      = data['nonce']
    pubkey     = data['pubkey']
    rsakv      = data['rsakv']
    pcid       = data['pcid']

    # 用户名：采用base64加密
    su = base64.b64encode(urllib.quote(src['username']))
    # 密码：采用rsa加密
    rsaPublickey= int(pubkey,16)
    key = rsa.PublicKey(rsaPublickey,65537)
    message = str(servertime) +'\t' + str(nonce) + '\n' + str(src['password'])
    sp = binascii.b2a_hex(rsa.encrypt(message,key))

    # 获取验证码图片
    captcha_URI = sess.get('http://login.sina.com.cn/cgi/pin.php?r=39011430&s=0&p='+pcid,
        headers={'Accept': config.accept_image})
    # 获取验证码字符串
    captcha = utils.crack_captcha(captcha_URI.content)
    print 'captcha:' + captcha

    payload = {
        'entry': 'weibo',
        'gateway': '1',
        'from': '',
        'savestate': '7',
        'userticket': '1',
        'pagerefer' : 'http://www.baidu.com/',
        'ssosimplelogin': '1',
        'vsnf': '1',
        'pcid':pcid,
        'door':captcha,
        'su': su,
        'service': 'miniblog',
        'servertime': servertime,
        'nonce': nonce,
        'pwencode': 'rsa2',
        'rsakv' : rsakv,
        'sp': sp,
        'sr':'1366*768',
        'prelt': '168',
        'encoding': 'UTF-8',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META'
    }
    resp = sess.post(url_login, data=payload,
        headers={
            'Referer':'http://weibo.com',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36'
    })
    retcode = re.findall(r'retcode=(\d+)',resp.content)[0]
    print 'retcode: '+ retcode
    if retcode == '0':
        return True
    else:
        reason = re.findall(r'reason=(.+)&',resp.content)[0]
        print 'reason: '+ urllib.unquote(reason).decode('GBK')
        return False

def post_sina_blog(post_url, src):
    """ 新浪博客发帖函数

    @param post_url:   板块地址 blog.sina.com.cn
    @type post_url:    str

    @param src:        用户名，密码，等等。
    @type src:         dict

    @return:           是否发帖成功
    @rtype:            bool

    """
    logger = utils.RAPLogger(post_url)
    sess = utils.RAPSession(src)

    # Step 1: 登录
    is_login = False
    i = 0
    while not is_login and i<src['TTL']:
        i += 1
        is_login = login_sina(sess, src)

    if not is_login:
        logger.error(' Login Error')
        return (False, str(logger))
    logger.info(' Login OK')

    resp = sess.get('http://control.blog.sina.com.cn/admin/article/article_add.php')

    soup = BeautifulSoup(resp.content)
    # 获取回复form
    form = soup.find('form', attrs={'id': 'editorForm'})
    payload = utils.get_datadic(form)
    payload['blog_title'] = src['subject']
    payload['blog_body'] = src['content']
    payload['conlen'] = 9
    payload['x_cms_flag'] = 0
    payload['x_rank'] = ''
    #print payload
    resp = sess.post(form['action'], data=payload)
    jsonData = json.loads(resp.content)
    logger.info(resp.content)
    if jsonData['code'] == u'B06001':
        url = 'http://blog.sina.com.cn/s/blog_'+jsonData['data']+'.html'
        logger.info(' Post OK')
        return (url, str(logger))
    while jsonData['code'] == u'B06013' and src['TTL']:
        src['TTL'] = src['TTL']-1
        captcha = sess.get('http://interface.blog.sina.com.cn/riaapi/checkwd_image.php?r=0.8578676988836378',
                              headers={
                                  'Accept': config.accept_image
                              })
        # 获取验证码字符串
        seccode = utils.crack_captcha(captcha.content)
        logger.info(' captcha:' + seccode)
        payload['checkword'] = seccode

        resp = sess.post(form['action'], data=payload)
        jsonData = json.loads(resp.content)
        logger.info(resp.content)
        if jsonData['code'] == u'B06001':
            url = 'http://blog.sina.com.cn/s/blog_'+jsonData['data']+'.html'
            logger.info(' Post OK')
            return (url, str(logger))

    logger.info(' Post Error')
    return ('', str(logger))

def reply_sina_club(post_url, src):
    """ 新浪论坛回复函数

        - Name:     新浪论坛18646492184
        - Feature:  (forum|club).*.sina.com.cn
        - Captcha:  YES
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

    # Step 1: 登录
    if not login_sina(sess, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.info(' Login OK')

    # Step 2: 回复
    resp = sess.get(post_url)
    host = utils.get_host(post_url)
    # 获取回复地址
    reply_url = re.findall(r'id=\"postform\" action=\"(.*?)\"',
                           resp.content)[0]
    soup = BeautifulSoup(resp.content)
    # 获取回复form
    form = soup.find('form', attrs={'id': 'postform'})
    # 构造回复参数
    payload = utils.get_datadic(form)
    payload['message'] = src['content'].decode('utf8').encode(CHARSET)
    # 替换回复地址中的特殊符号
    reply_url = reply_url.replace('&amp;', '&')
    # 发送回复post包
    resp = sess.post(reply_url, data=payload,
                           headers={
                               'Origin': utils.get_host(post_url),
                               'Referer': post_url
                           })
    post_times = 0
    # 验证是否成功，如果失败再次发送
    # 失败可能原因：验证码错误
    while 'postform' not in resp.content \
            and post_times < src['TTL']:
        # 限制最大发送次数
        post_times = post_times + 1
        logger.info(' reply need captcha')
        # 获取验证码图片
        captcha = sess.get(host + 'seccode.php',
                              headers={
                                  'Accept': config.accept_image,
                                  'Referer': reply_url
                              })
        # 获取验证码字符串
        seccode = utils.crack_captcha(captcha.content)
        logger.info(' seccode:' + seccode)
        # 回复参数中增加验证码
        payload['seccodeverify'] = seccode.decode(CHARSET)
        # 发送回复post包
        resp = sess.post(reply_url, data=payload,
                               headers={
                                   'Origin': utils.get_host(post_url),
                                   'Referer': post_url
                               })
    # 若指定字样出现在response中，表示回复成功
    if 'postform' not in resp.content:
        logger.error(' Reply Error')
        return (False, str(logger))
    logger.info(' Reply OK')
    return (True, str(logger))


def reply_sina_news(post_url, src):
    """ 新浪新闻回复函数

        - Name:     新浪新闻
        - Feature:  ^http://[^(c|f)].*.sina.com.cn
        - Captcha:  YES
        - Login:    YES

    @param post_url:   新浪地址
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict
    
    @return:           是否回复成功
    @rtype:            bool

    """
    logger = utils.RAPLogger(post_url)
    sess = utils.RAPSession(src)
    resp = sess.get(post_url)

    # Step 1: 登录
    if not login_sina(sess, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.info(' Login OK')

    # Step 2: 回复
    # 频道id
    channel = re.findall(r'channel:.*\'(.*?)\'', resp.content)[0]
    # 新闻id
    newsid = re.findall(r'newsid:.*\'(.*?)\'', resp.content)[0]

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
    resp = sess.post(reply_url, data=payload,
                           headers={
                               'Referer': post_url
                           })
    # 若指定字样出现在response中，表示回复成功
    if 'result' not in resp.content:
        logger.error(' Reply Error')
        return (False, str(logger))
    logger.info(' Reply OK')
    return (True, str(logger))

def get_account_info_sina_club(src):
    """ 新浪账户信息获取函数

    @param src:        用户名，密码
    @type src:         dict

    @return:           账户信息
    @rtype:            dict
    """
    logger = utils.RAPLogger(src['username'])
    sess = utils.RAPSession(src)

    # Step 1: 登录
    if not login_sina(sess, src):
        logger.error(' Login Error')
        return ({}, str(logger))
    logger.info(' Login OK')

    resp = sess.get('http://club.mil.news.sina.com.cn/memcp.php')

    soup = BeautifulSoup(resp.content)
    head_image = soup.select('div.avatar img')[0]['src']

    html = resp.content.decode(CHARSET).encode('utf8')
    account_score = re.findall(r'<li>积分: (\d+)</li>', html)[0]
    account_class = re.findall(r'<label>用户组:</label> <font color="green">(.*?)</font>', html)[0]

    time_register = re.findall(r'<label>注册日期:</label>(.*?)</li>', html)[0]
    time_last_login = re.findall(r'<label>上次访问:</label>(.*?)</li>', html)[0]

    login_count = ''

    count_post = re.findall(r'<li>帖子: (\d+)', html)[0]
    count_reply = re.findall(r'<li>精华: (\d+)', html)[0]

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
