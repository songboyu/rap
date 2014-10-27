# -*- coding: utf-8 -*-
"""凯迪回复模块

@author: HSS
@since: 2014-10-20
@summary: 凯迪社区

@var CHARSET: 凯迪社区网页编码
@type CHARSET: String

"""
import re

from bs4 import BeautifulSoup

import utils

CHARSET = 'gb2312'

def reply_kdnet(post_url, src):
    """ 凯迪社区回复函数

        - Name:     凯迪社区
        - Feature:  club.kdnet.net
        - Captcha:  NO
        - Login:    NO

    @param post_url:   帖子地址
    @type post_url:    String

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dictionary
    
    @return:           是否回复成功
    @rtype:            boolean

    """
    logger = utils.RAPLogger(post_url)
    session = utils.RAPSession(src)
    request = session.get(post_url)

    # 获得回复iframe
    iframe = re.findall('<iframe src=\"(.*?)\"', request.content)[0]
    request = session.get(iframe.decode(CHARSET))
    soup = BeautifulSoup(request.content)
    # 获得回复form
    form = soup.find('form', attrs={'id': 't_form'})
    # 获得boardid，作为post参数
    boardid = re.findall(r'boardid=(.*\d)', post_url)[0]
    # 构造回复参数
    payload = utils.get_datadic(form)
    payload['UserName'] = src['username']
    payload['password'] = src['password']
    payload['body'] = src['content'].decode('utf8').encode(CHARSET)
    # 回复地址
    reply_url = 'http://upfile1.kdnet.net/do_lu_shuiyin.asp?'\
        + 'action=sre&method=fastreply&BoardID='
    # 发送回复post包
    request = session.post(reply_url + boardid, data=payload)
    # 若指定字样出现在response中，表示回复成功
    if u'成功回复'.encode(CHARSET) not in request.content:
        logger.error(' Reply Error')
        return (False, str(logger))
    logger.debug(' Reply OK')
    return (True, str(logger))
