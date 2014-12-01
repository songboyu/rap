# -*- coding: utf-8 -*-
"""凯迪社区模块

@author: HSS
@since: 2014-10-20
@summary: 凯迪社区

@var CHARSET: 凯迪社区网页编码
@type CHARSET: str

"""
import re

from bs4 import BeautifulSoup

import utils

CHARSET = 'gb2312'
def login_kdnet(sess, src):
    """ 凯迪社区登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    payload = {
        'a':'login',
        'username':src['username'],
        'password':src['password'],
        'last_url':'http://user.kdnet.net/'
    }
    # 发送登录post包
    resp = sess.post('http://user.kdnet.net/user.asp', data=payload)
    # 若指定字样出现在response中，表示登录成功
    if 'msg' in resp.content:
        return False
    return True


def reply_kdnet(post_url, src):
    """ 凯迪社区回复函数

        - Name:     凯迪社区
        - Feature:  club.kdnet.net
        - Captcha:  NO
        - Login:    NO

    @param post_url:   帖子地址
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict
    
    @return:           是否回复成功
    @rtype:            bool

    """
    logger = utils.RAPLogger(post_url)
    sess = utils.RAPSession(src)
    resp = sess.get(post_url)

    # 获得回复iframe
    iframe = re.findall('<iframe src=\"(.*?)\"', resp.content)[0]
    resp = sess.get(iframe.decode(CHARSET))
    soup = BeautifulSoup(resp.content)
    # 获得回复form
    form = soup.find('form', attrs={'id': 't_form'})
    # 获得boardid，作为post参数
    boardid = re.findall(r'boardid=(.*\d)', post_url)[0]
    # 构造回复参数
    payload = utils.get_datadic(form)
    payload['UserName'] = src['username'].decode('utf8').encode(CHARSET)
    payload['password'] = src['password'].decode('utf8').encode(CHARSET)
    payload['body'] = src['content'].decode('utf8').encode(CHARSET)
    # 回复地址
    reply_url = 'http://upfile1.kdnet.net/do_lu_shuiyin.asp?'\
        + 'action=sre&method=fastreply&BoardID='
    # 发送回复post包
    resp = sess.post(reply_url + boardid, data=payload)
    print resp.content.decode(CHARSET)
    # 若指定字样出现在response中，表示回复成功
    if u'成功回复'.encode(CHARSET) not in resp.content:
        logger.error(' Reply Error')
        return (False, str(logger))
    logger.info(' Reply OK')
    return (True, str(logger))

def post_kdnet(post_url, src):
    """ 凯迪社区发主贴函数

        - Name:     凯迪社区
        - Feature:  club.kdnet.net
        - Captcha:  NO
        - Login:    NO

    @param post_url:   板块地址 如：http://club.kdnet.net/list.asp?boardid=2
    @type post_url:    str

    @param src:        用户名，密码，标题，主帖内容，等等。
    @type src:         dict

    @return:           是否发帖成功，帖子URL
    @rtype:            bool,str

    """
    logger = utils.RAPLogger(post_url)
    sess = utils.RAPSession(src)
    # Step 1: 登录
    if not login_kdnet(sess, src):
        logger.error(' Login Error')
        return (False, '', str(logger))
    logger.info(' Login OK')

    # 获得boardid，作为post参数
    boardid = re.findall(r'boardid=(\d*)',post_url)[0]
    resp = sess.get('http://upfile1.kdnet.net/textareaeditor/post_ubb.asp?action=new&boardid='+boardid)
    soup = BeautifulSoup(resp.content)
    # 获得发帖form
    form = soup.find('form', attrs={'id': 'Dvform'})
    # 构造回复参数
    payload = utils.get_datadic(form)
    payload['topic'] = src['subject'].decode('utf8').encode(CHARSET)
    payload['body'] = src['content'].decode('utf8').encode(CHARSET)
    payload['font1'] = u'[原创]'.encode(CHARSET)
    # 发送发帖post包
    resp = sess.post('http://upfile1.kdnet.net/SavePost_ubb.asp?Action=snew&boardid=' + boardid, data=payload)

    # print resp.content.decode(CHARSET)
    # 若指定字样出现在response中，表示发帖成功
    if u'发帖成功'.encode(CHARSET) not in resp.content:
        logger.error(' Post Error')
        return (False, '', str(logger))
    logger.info(' Post OK')
    url = re.findall(r'var url="(.*?)"',resp.content)[0]
    logger.info(url)
    return (True, url, str(logger))

def get_account_info_kdnet(src):
    """ 凯迪社区账户信息获取函数

    @param src:        用户名，密码
    @type src:         dict

    @return:           账户信息
    @rtype:            dict
    """
    logger = utils.RAPLogger(src['username'])
    sess = utils.RAPSession(src)

    faild_info = {'Error':'Failed to get account info'}
    # Step 1: 登录
    if not login_kdnet(sess, src):
        logger.error(' Login Error')
        return (faild_info, str(logger))
    logger.info(' Login OK')

    resp = sess.get('http://user.kdnet.net/index.asp')
    head_image = re.findall(r'<img id=\"userface_img_index\" onerror=\"this.src = duf_190_190;\" src=\"(.*?)\"', resp.content)[0]

    account_score = ''
    account_class = ''

    content = resp.content.decode(CHARSET).encode('utf8')
    # print content
    time_register = re.findall(r'注册时间：(.*?)<', content)[0]
    time_last_login = re.findall(r'上次登录：(.*?)<', content)[0]
    login_count = re.findall(r'登录次数：(\d*)<', content)[0]

    resp = sess.get('http://user.kdnet.net/posts.asp')
    content = resp.content
    if u'还未发表内容'.encode(CHARSET) in content:
        count_post = 0
    else:
        count_post = re.findall(ur'共(\d*)条记录'.encode(CHARSET), content)[0]


    resp = sess.get('http://user.kdnet.net/reply.asp')
    content = resp.content
    if u'还未发表内容'.encode(CHARSET) in content:
        count_reply = 0
    else:
        count_reply = re.findall(ur'共(\d*)条记录'.encode(CHARSET), content)[0]

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
    return (account_info, str(logger))
