# -*- coding: utf-8 -*-
"""澳洲联合网模块

@author: HSS
@since: 2014-10-20
@summary: 澳洲联合网

@var CHARSET: 澳洲联合网网页编码
@type CHARSET: str

"""
import re

from bs4 import BeautifulSoup

import utils

CHARSET = 'utf8'

def reply_unitedtimes(post_url, src):
    """ 澳洲联合网回复函数

        - Name:     澳洲联合网
        - Feature:  unitedtimes.com.au/
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
    form = soup.find('form', attrs={'method': 'post'})
    # 构造回复参数
    payload = utils.get_datadic(form)
    payload['content'] = src['content']
    # 发送回复post包
    resp = sess.post(form['action'], data=payload)
    # 若指定字样出现在response中，表示回复成功
    if '操作成功' not in resp.content:
        logger.error(' Reply Error')
        return (False, str(logger))
    logger.info(' Reply OK')
    return (True, str(logger))