# -*- coding: utf-8 -*-
"""参与网回复模块

@author: sky
@since: 2015-01-05
@summary: 参与网
"""

from bs4 import BeautifulSoup
from utils import get_datadic
from utils import get_host
from utils import RAPSession
from utils import RAPLogger

# Coding: gb2312
# Captcha: not required
# Login: not required
CHARSET = 'GBK'
def reply_canyu(post_url, src):
    """参与网回帖模块
    @author: sky
    @since: 2015-01-05

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   帖子地址
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool
    """

    logger = RAPLogger(post_url)

    host = get_host(post_url)
    sess = RAPSession(src)

    # Step 1: 获取回帖页面
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'remarkForm'})
    
    # Step 2: 提交回帖
    # 回复内容
    payload = {}
    payload = get_datadic(form)
    payload['face'] = '1'
    payload['body'] = src['content'].decode('utf8').encode(CHARSET)
    payload['username'] = src['username'].decode('utf8').encode(CHARSET)
    #发送post包
    resp = sess.post(host + form['action'], data=payload)
    #再次请求原网页，查看是否已经有回帖内容
    resp = sess.get(post_url)
    #判断回帖后页面是否含有回帖内容，若存在则证明回帖成功，否则失败
    if src['content'].decode('utf8').encode(CHARSET) in resp.content:
        logger.info('Reply OK')
    else:
        logger.error('Reply Error, please try again !')
        return (False, str(logger))
    return (True, str(logger))
