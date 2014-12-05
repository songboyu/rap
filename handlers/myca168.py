# -*- coding: utf-8 -*- 

import requests, re, random, logging
from bs4 import BeautifulSoup
import urllib
import config
from utils import *
import utils
from utils import get_datadic

# Coding: utf8
# Captcha: not required
# Login: required


def login_myca168(post_url, s, src):
    """天涯信息登录模块

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    host = utils.get_host(post_url)
    r = s.get(host)
    
    payload = {
        'login':src['username'],
        'password':src['password']
    }
    # 发送post包
    r = s.post(host + 'login/login/', data=payload,
        headers = {
            'Origin':'http://www.myca168.com',
            'Referer':'http://www.myca168.com/index/index/',
            'X-Requested-With':'XMLHttpRequest'
        })
    # 若指定字样出现在response中，表示登录成功
    if 'yes' not in r.content:
        return False    
    return True
# Coding: utf8
# Captcha: not required
# Login: required
def post_myca168_forum(post_url, src):
    """天涯信息论坛发主贴模块

    @author: sky
    @since: 2014-12-02

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   帖子地址 http://www.myca168.com/bbs/index/post/id/9
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。tyui,tyui
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool
    """
    logger = utils.RAPLogger(post_url)
    host = utils.get_host(post_url)
    s = utils.RAPSession(src)

    # 登录
    if not login_myca168(post_url, s, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.info(' Login OK')
   
    payload ={
        'MAX_FILE_SIZE':(None,'134217728'),
        'title':(None,src['subject']),
        'editor1':(None,'<p>'+src['content']+'</p>'),
        'submit':(None,u'提交'),
        'image':('a.png','','application/octet-stream')
    }
    # payload['MAX_FILE_SIZE']='134217728'
    # payload['title'] = src['subject']
    # payload['editor1'] = '<p>'+src['content']+'</p>'
    # payload['submit'] = u'提交'

    # 发送发主贴post包
    resp = s.post(post_url, files=payload)
    print resp.url
    # 若指定字样出现在response中，表示发帖成功
    if src['subject'] not in resp.content:
        # logger.info(resp.content)
        logger.error(' Post Error')
        return (False, '', str(logger))
    logger.info(' Post OK')
    href = re.findall(r'<td><a href="(.*?)">', resp.content)[1]
    url = host + href
    logger.info(url)
    return (True, '', str(logger))