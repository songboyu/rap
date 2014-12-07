# -*- coding: utf-8 -*-
"""凯迪社区模块

@author: HSS
@since: 2014-10-20
@summary: 独立中文笔会

@var CHARSET: 独立中文笔会网页编码
@type CHARSET: str

"""
import re

from bs4 import BeautifulSoup

import utils

CHARSET = 'utf8'

def reply_penchinese_blog(post_url, src):
    """ 凯迪社区回复函数

        - Name:     独立中文笔会
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

    soup = BeautifulSoup(resp.content)
    # 获得回复form
    form = soup.find('form', attrs={'id': 'commentform'})
    # 构造回复参数
    payload = utils.get_datadic(form)
    payload['author'] = src['username']
    payload['email'] = src['password']
    payload['comment'] = src['content']
    # 发送回复post包
    resp = sess.post(form['action'], data=payload)
    print resp.url
    # 若指定字样出现在response中，表示回复成功
    if resp.url == form['action']:
        logger.error(' Reply Error')
        return (False, str(logger))
    logger.info(' Reply OK')
    return (True, str(logger))
