# -*- coding: utf-8 -*-
"""消息树模块

@author: HSS
@since: 2014-10-20
@summary: 消息树

@var CHARSET: 消息树网页编码
@type CHARSET: str

"""
import re

from bs4 import BeautifulSoup

import utils

CHARSET = 'gbk'
def login_enewstree(post_url, sess, src):
    """ 消息树登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    # 获得回复form
    form = soup.find('form', attrs={'id': 'lsform'})
    # 构造回复参数
    payload = utils.get_datadic(form)
    payload['username'] = src['username'].decode('utf8').encode(CHARSET)
    payload['password'] = src['password'].decode('utf8').encode(CHARSET)
    # 发送登录post包
    resp = sess.post('http://enewstree.com/discuz/'+form['action'], data=payload,
                     headers = {
                         'Referer':post_url
                     })
    # 若指定字样出现在response中，表示登录成功
    if src['username'].decode('utf8') not in resp.content.decode(CHARSET):
        return False
    return True

def post_enewstree_forum(post_url, src):
    """ 消息树发主贴函数

    @param post_url:   板块地址 如：http://enewstree.com/discuz/forum.php?mod=forumdisplay&fid=47
    @type post_url:    str

    @param src:        用户名，密码，标题，主帖内容，等等。
    @type src:         dict

    @return:           是否发帖成功，帖子URL
    @rtype:            bool,str

    """
    logger = utils.RAPLogger(post_url)
    sess = utils.RAPSession(src)
    # Step 1: 登录
    if not login_enewstree(post_url, sess, src):
        logger.error(' Login Error')
        return ('', str(logger))
    logger.info(' Login OK')

    fid = re.findall(r'fid=(\d*)', post_url)[0]
    resp = sess.get('http://enewstree.com/discuz/forum.php?mod=post&action=newthread&fid='+fid)
    formhash = re.findall(r'formhash=(.*?)"', resp.content)[0]
    print formhash
    payload = {
        'formhash':formhash,
        'posttime':'1417366974',
        'wysiwyg':'1',
        'subject':src['subject'].decode('utf8').encode(CHARSET),
        'message':src['content'].decode('utf8').encode(CHARSET),
        'allownoticeauthor':'1',
        'usesig':'1',
        'secqaahash':'qSxqZkkW',
        'secanswer':'1776',
        'seccodehash':'cSxqZkkW',
        'seccodemodid':'forum::post',
        'seccodeverify':'ec48',
        'save':'',
        'uploadalbum':'-2',
        'newalbum':'',
    }
    # 发送登录post包
    resp = sess.post('http://enewstree.com/discuz/forum.php?mod=post&action=newthread&fid='+fid
                     +'&extra=&topicsubmit=yes',
                     data=payload,
                     headers = {
                         'Referer':post_url
                     })
    # 若指定字样出现在response中，表示回复成功
    if src['content'].decode('utf8') not in resp.content.decode(CHARSET):
        logger.error(' Post Error')
        return ('', str(logger))
    logger.info(' Post OK')
    url = resp.url
    print url
    return (url, str(logger))
