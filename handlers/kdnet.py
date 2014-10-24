# -*- coding: utf-8 -*-
"""凯迪回复模块

* Author: songboyu
* Modify: 2014-10-20
* Coding: gb2312
* Contain：凯迪社区

"""
import re

from bs4 import BeautifulSoup

import utils

# 凯迪社区网页编码
CODING = 'gb2312'

# name:     凯迪社区
# Feature:  club.kdnet.net
# Captcha:  not required
# Login:    not required
def reply_kdnet(post_url, src):
    """凯迪社区回复函数

    :param post_url:   帖子地址
    :param src:        {username, password, content etc.}
    :return:           success? True:False

    """
    logger = utils.RAPLogger(post_url)
    session = utils.RAPSession(src)
    response = session.get(post_url)

    # 获得回复iframe
    iframe = re.findall('<iframe src=\"(.*?)\"', response.content)[0]
    response = session.get(iframe.decode(CODING))
    soup = BeautifulSoup(response.content)
    # 获得回复form
    form = soup.find('form', attrs={'id': 't_form'})
    # 获得boardid，作为post参数
    boardid = re.findall(r'boardid=(.*\d)', post_url)[0]
    # 构造回复参数
    payload = utils.get_datadic(form)
    payload['UserName'] = src['username']
    payload['password'] = src['password']
    payload['body'] = src['content'].decode('utf8').encode(CODING)
    # 回复地址
    reply_url = 'http://upfile1.kdnet.net/do_lu_shuiyin.asp?'\
              +'action=sre&method=fastreply&BoardID='
    # 发送回复post包
    response = session.post(reply_url + boardid, data=payload)
    # 若指定字样出现在response中，表示回复成功
    if u'成功回复'.encode(CODING) not in response.content:
        logger.error(' Reply Error')
        return (False, str(logger))
    logger.debug(' Reply OK')
    return (True, str(logger))
