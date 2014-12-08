# -*- coding: utf-8 -*-
"""飞月网新闻回复模块

@author: sky
@since: 2014-12-08
@summary: 飞月网新闻
"""

from bs4 import BeautifulSoup
from hashlib import md5
from utils import get_datadic
from utils import get_host
from utils import RAPSession
from utils import RAPLogger
import urllib
import random

# Coding: utf8
# Captcha: not required
# Login: not required
def reply_onmoon_news(post_url, src):
    """飞月网新闻回复模块
    @author: sky
    @since: 2014-12-08

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   帖子地址  http://www.onmoon.com/chs/2014/11/30/800307.html
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    logger = RAPLogger(post_url)

    host = get_host(post_url)
    sess = RAPSession(src)
    
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)

    name = soup.find('input', attrs={'id': 'plid'})
    name1 = name.attrs['value']
    payload = {}
    payload['']=src['content']
    u= urllib.urlencode(payload)
    resp = sess.get(host + 'pl.php?nid=' + name1 + '&pl=' + u[1:]+ '&randomnumber=' + str(random.randint(1000,9999)))
    
    #再次请求原网页，查看是否已经有回帖内容
    resp = sess.get(post_url)

    #with open('1.html', 'w') as f:
    #    f.write(resp.content)
    #判断回帖后页面是否含有回帖内容，若存在则证明回帖成功，否则失败
    if src['content'] in resp.content:
        logger.info('Reply OK')
    else:
        logger.error('Reply Error')
        return (False, str(logger))
    return (True, str(logger))
    