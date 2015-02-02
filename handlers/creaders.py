# -*- coding: utf-8 -*- 
"""
@author: sky
@since: 2014-11-25
@summary: 万维

@var CHARSET: 万维网页编码
@type CHARSET: str
"""

import re

from bs4 import BeautifulSoup

import config
import utils

"""

@author: sky
@since: 2014-11-25
@summary: 万维论坛

@var CHARSET: 万维网页编码
@type CHARSET: str

"""
CHARSET = 'GBK'
def login_creaders_forum(post_url,sess, src):
    """万维论坛登录模块

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    url = post_url.rpartition('/')[0]+'/'
    payload = {
        'act':'login',
        'user_name':src['username'],
        'user_password':src['password'],
        'frm_id':'undefined',
        'captcha':''
    }
    # 发送登录post包
    resp = sess.get(url+'ajax.forum.php?url=?', params=payload)
    # 若指定字样出现在response中，表示登录成功
    if src['username'] not in resp.content:
        return False
    return True

# Coding: gb2312
# Captcha: not required
# Login: required
def reply_creaders_news(post_url, src):
    logger = utils.RAPLogger(post_url)
    host = utils.get_host(post_url)
    s = utils.RAPSession(src)

    r = s.get(post_url)
    payload = {
    	'news_id': re.findall('news_id=(\d+)', r.content)[0],
    	'r_nid': re.findall('r_nid=(\d+)', r.content)[0],
    	'username': src['username'],
    	'password': src['password'],
    	'replyid': 0,
    	# The charset of this page is `gb2312` absolutely, but it seems that
    	# `saytext` receives `utf8` only.
    	'saytext': src['content'],
    }
    r = s.post(host + '/headline/postcomment.php', data=payload)
    if u'评论成功'.encode('gb2312') not in r.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))

def reply_creaders_forum(post_url, src):
    """万维论坛回复模块
    @author: sky
    @since: 2014-11-27
    @param post_url:   帖子地址
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """

    logger = utils.RAPLogger(post_url)
    sess = utils.RAPSession(src)

    # step 2: 获取回帖页面
    resp = sess.get(post_url)

    # step 3: 提交回帖
    # 回复内容
    payload = {
        'user_name2':src['username'].decode('utf8').encode(CHARSET),
        'user_password2':src['password'].decode('utf8').encode(CHARSET),
        'captcha':'',
        'btrd_subject':src['content'].decode('utf8').encode(CHARSET),
        'btrd_content':src['content'].decode('utf8').encode(CHARSET)
    }
    # 发送post包
    resp = sess.post(post_url, data=payload)
    #判断回帖后页面是否含有回帖内容，若存在则证明回帖成功，否则失败
    if src['content'].decode('utf8').encode(CHARSET) in resp.content:
        logger.info('Reply OK')
    else:
        logger.error('Reply Error')
        return (False, str(logger))
    return (True, str(logger))

# Coding: gb2312
# Captcha: not required
# Login:  required
def post_creaders_forum(post_url, src):
    """万维论坛发主贴模块

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   帖子地址 如：http://bbs.creaders.net/life/
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    logger = utils.RAPLogger(post_url)
    sess = utils.RAPSession(src)

    url = post_url.rpartition('/')[0]+'/'
    resp = sess.get(url+'post.php?')
    # 构造回复参数
    payload = {
        'user_name2':src['username'].decode('utf8').encode(CHARSET),
        'user_password2':src['password'].decode('utf8').encode(CHARSET),
        'captcha':'',
        'trd_subject':src['subject'].decode('utf8').encode(CHARSET),
        'trd_content':src['content'].decode('utf8').encode(CHARSET)
    }
    # 发送发主贴post包
    resp = sess.post(url+'post.php?', data=payload)
    content = resp.content.decode(CHARSET).encode('utf8')
    
    # By sniper 2015-2-1
    # 标题中的'('和')'等需要在正则表达式中转义
    # 如：[转帖]ZT) 汉服是FQ闹的大笑话
    subject = re.escape(src['subject'])
    href = re.findall(r'<a href=\'(.*?)\' class=\'thread_title\'>'+subject, content)[0]
    url = post_url + href
    # 如果url未成功匹配，则抛出异常，Post Error
    
    logger.info('Post OK')
    return (url, str(logger))
    