# -*- coding: utf-8 -*-
"""搜狐回复模块

@author: HSS
@since: 2014-10-20
@summary: 搜狐新闻

@var CHARSET: 搜狐网页编码
@type CHARSET: str

"""
import re
import time
from hashlib import md5

from bs4 import BeautifulSoup

import config
import utils

CHARSET = 'gb2312'
def login_sohu(sess, post_url, src):
    """ 搜狐登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   帖子地址
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    logger = utils.RAPLogger(post_url)
    # 登录地址
    login_url = 'https://passport.sohu.com/sso/login.jsp'
    # 发送登录post包
    payload = {
        'userid':src['username'],
        'password':md5(src['password']).hexdigest(),
        'appid':'1019',
        'persistentcookie':'1',
        's':int(time.time())*1000,
        'b':'7',
        'w':'1366',
        'pwdtype':'1',
        'v':'26'
    }
    headers = {
        'Host':'passport.sohu.com',
        'Referer':'http://i.sohu.com/login/logon.do',
        'User-Agent':config.user_agent
    }
    resp = sess.get(login_url, params=payload, headers=headers)
    logger.info(' info: '+resp.content)
    # 若指定字样出现在response中，表示登录成功
    if 'success' not in resp.content:
        return False
    resp = sess.get('http://uis.i.sohu.com/api/passport/slogin.do')
    logger.info(resp.content)
    return True

def reply_sohu_news(post_url, src):
    """ 搜狐新闻回复函数

        - Name:     搜狐新闻
        - Feature:  ^http://[^(c|f)].*.sina.com.cn
        - Captcha:  YES
        - Login:    YES

    @param post_url:   搜狐地址
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict
    
    @return:           是否回复成功
    @rtype:            bool

    """
    logger = utils.RAPLogger(post_url)
    sess = utils.RAPSession(src)

    # Step 1: 登录
    if not login_sohu(sess, post_url, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.info(' Login OK')

    # Step 2: 回复
    resp = sess.get(post_url)

    title = re.findall(r'<title>(.*?)</title>',resp.content)[0]
    topicsid = re.findall(r'var entityId =\s*(\d*)',resp.content)[0]
    appid = 'cyqemw6s1'
    conf = 'prod_0266e33d3f546cb5436a10798e657d97'
    jump_url = re.findall(r'jumpUrl: \'(.*?)\'',resp.content)[0]
    page_conf = re.findall(r'var _config = (\s|\S)*?\}[\s|\S]*?[w|\(fun]',resp.content)[0]

    comments_url = 'http://quan.sohu.com/pinglun/cyqemw6s1/' + topicsid
    logger.info(' comments_url: '+comments_url)

    payload ={
        't':int(time.time())*1000,
        'callback':'fn',
        'appid':appid,
        'conf':conf,
        'confstr':conf,
        'client_id':appid,
        'title':title,
        'topicurl':post_url,
        'topicsid':topicsid,
        'hideList':'true',
        'hideSubList':'true',
        'cyanTitle':'',
        'jumpUrl':jump_url,
        'varName':topicsid,
        'customSohu':'true',
        'pageSize':10,
        'category_id':'',
        'commentHide':'true',
        'spSize':5,
        'pageConf':page_conf
    }
    resp = sess.get('http://changyan.sohu.com/node/html', params=payload)
    topicid = re.findall(r'"topic_id":(\d*)',resp.content)[0]
    logger.info(' topicid: '+topicid)
    # 回复地址
    reply_url = 'http://changyan.sohu.com/api/2/comment/submit'
    payload = {
        'client_id':appid,
        'topic_id':'364211617',
        'content':src['content'],
        'cmt_bold':'false',
        'cmt_color':'false',
        'dataType':'',
        'cmtNum':'',
        'floorNum':'',
        'attachment_urls':'',
    }
    # 发送回复post包
    resp = sess.post(reply_url, data=payload,
                     headers={
                         'Accept':'application/json, text/javascript, */*; q=0.01',
                         'Host':'changyan.sohu.com',
                         'Origin':'http://quan.sohu.com',
                         'Referer': comments_url
                     })
    logger.info(resp.content)
    comment_id = re.findall(r'{"id":(\d*)}',resp.content)[0]

    # 若指定字样出现在response中，表示回复成功
    if comment_id == '0':
        logger.error(' Reply Error')
        return (False, str(logger))

    payload = {
        'callback':'fn',
        'comment_id':comment_id,
        'client_id':appid,
        'topic_id':'364211617',
        '_':int(time.time())*1000
    }
    resp = sess.get('http://changyan.sohu.com/api/2/comment/floor',params=payload,
                    headers={
                         'Host':'changyan.sohu.com',
                         'Origin':'http://quan.sohu.com',
                         'Referer': comments_url
                     })
    logger.info(resp.content)
    logger.info(' Reply OK')
    return (True, str(logger))
