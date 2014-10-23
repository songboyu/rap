__author__ = 'boyu'
# -*- coding: utf-8 -*-
import urllib
import requests, re
from bs4 import BeautifulSoup
import config
from utils import *
import random

# Coding: gb2312
# Captcha: not required
# Login: required
def reply_163_blog(post_url, src):
    logger = RAPLogger(post_url)
    host = 'http://reg.163.com/'
    s = RAPSession(src)

    # Step 1: Login
    r = s.get(host)
    soup = BeautifulSoup(r.content)
    form = soup.find('form', attrs={'id': 'fLogin'})
    payload = get_datadic(form)
    payload['username'] = src['username']
    payload['password'] = src['password']

    r = s.post('https://reg.163.com/logins.jsp', data=payload)
    r = s.get('http://reg.163.com/Main.jsp?username=ajsdhsjdfoo')

    if '上次登录情况' not in r.content:
        logger.error(' Login Error')
        return (False, str(logger))
    logger.debug(' Login OK')


    # Step 2: 验证码
    r = s.get('http://api.blog.163.com/cap/captcha.jpgx?parentId=241151032&r=',
        headers={
            'Accept': config.accept_image,
            'Referer': post_url,
        })
    seccode = crack_captcha(r.content)
    logger.debug(' seccode:'+seccode)


    # Step 3: 提交回复
    r = s.get(post_url)
    soup = BeautifulSoup(r.content)
    meta = soup.find('meta', attrs={'name': 'author'})

    id = re.findall('id:\'(.*?)\'', r.content)[0]
    parentId = re.findall('parentId=(.*?)&', r.content)[0]
    author_0 =  urllib.quote(meta.attrs['content'].split(',')[0].encode('gbk'))
    author_1 =  urllib.quote(meta.attrs['content'].split(',')[1].encode('gbk'))
    content = urllib.quote(src['content']+'<wbr>')
    payload ='''callCount=1
scriptSessionId=${scriptSessionId}187
c0-scriptName=BlogBeanNew
c0-methodName=addBlogComment
c0-id=0
c0-e1=string:'''+id+'''
c0-e2=number:'''+parentId+'''
c0-e3=string:
c0-e4=string:'''+content+'''
c0-e5=string:'''+src['username']+'''
c0-e6=string:
c0-e7=number:-1
c0-e8=number:-1
c0-e9=number:'''+parentId+'''
c0-e10=string:'''+author_0+'''
c0-e11=string:'''+author_1+'''
c0-e12=boolean:true
c0-param0=Object_Object:{blogId:reference:c0-e1,blogUserId:reference:c0-e2,blogTitle:reference:c0-e3,content:reference:c0-e4,publisherNickname:reference:c0-e5,publisherEmail:reference:c0-e6,mainComId:reference:c0-e7,replyComId:reference:c0-e8,replyToUserId:reference:c0-e9,replyToUserName:reference:c0-e10,replyToUserNick:reference:c0-e11,synchMiniBlog:reference:c0-e12}
c0-param1=string:'''+seccode+'''
c0-param2=boolean:false
batchId=118652'''
    headers = {'Content-Type':'text/plain',
               'Origin':'http://api.blog.163.com',
               'Referer':'http://api.blog.163.com/crossdomain.html?t=20100205',
               'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6'}
    r = s.post('http://api.blog.163.com/xinluduwu/dwr/call/plaincall/BlogBeanNew.addBlogComment.dwr', data=payload, headers=headers)

    if '_remoteHandleCallback' not in r.content:
        logger.error(' Reply Error')
        return (False, str(logger))
    logger.debug(' Reply OK')
    return (True, str(logger))

def reply_163_news(post_url, src):
    logger = RAPLogger(post_url)
    host = 'http://reg.163.com/'
    s = RAPSession(src)

    # Step 1: Login
    r = s.get(host)
    soup = BeautifulSoup(r.content)
    form = soup.find('form', attrs={'id': 'fLogin'})
    payload = get_datadic(form)
    payload['username'] = src['username']
    payload['password'] = src['password']

    r = s.post('https://reg.163.com/logins.jsp', data=payload)
    r = s.get('http://reg.163.com/Main.jsp?username=ajsdhsjdfoo')

    if '上次登录情况' not in r.content:
        logger.error(' Login Error')
        return (False, str(logger))
    logger.debug(' Login OK')


    # Step 2: 验证码
    r = s.get(post_url)
    boardId = re.findall('boardId = \"(.*?)\"', r.content)[0]
    threadId = re.findall('threadId = \"(.*?)\"', r.content)[0]
    commentsURL = "http://comment.news.163.com/" + boardId + "/" + threadId + ".html"

    headers = {'X-Requested-With':'XMLHttpRequest',
               'Origin':'http://comment.news.163.com',
               'Referer':commentsURL,
               'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6'
    }

    r = s.get('http://comment.news.163.com/reply/needvalidate.jsp?time=1413303328581',headers=headers)
    needValidate = re.findall('needValidate:(.*?),', r.content)[0]
    seccode = 0
    if needValidate == '1':
        r = s.get('http://comment.news.163.com/reply/auth/validatecode.jsp?rnd=',
            headers={
                'Accept': config.accept_image,
                'Referer': commentsURL,
            })
        seccode = crack_captcha(r.content)
        logger.debug(' seccode:'+seccode)
        r = s.get('http://comment.news.163.com/reply/isValidateCodeValid.jsp?validateCode='+seccode,
            headers={
                'Referer': commentsURL,
            })
        logger.debug(' '+r.content)

    # r = s.get(commentsURL+'#replyForm')
    payload = {
        'board':boardId,
        'quote':'',
        'threadid':threadId,
        'hidename':False,
        'username':src['username'],
        'body':src['content'],
        'isTinyBlogSyn':1,
        'flag':'',
        'validateCode':seccode,
    }

    r = s.post('http://comment.news.163.com/reply/dopost.jsp',data=payload, headers=headers)
    if '网易首页' not in r.content:
        logger.error(' Reply Error')
        return (False, str(logger))
    logger.debug(' Reply OK')
    return (True, str(logger))

def reply_163_bbs(post_url, src):
    logger = RAPLogger(post_url)
    host = 'http://reg.163.com/'
    s = RAPSession(src)

    # Step 1: Login
    r = s.get(host)
    soup = BeautifulSoup(r.content)
    form = soup.find('form', attrs={'id': 'fLogin'})
    payload = get_datadic(form)
    payload['username'] = src['username']
    payload['password'] = src['password']

    r = s.post('https://reg.163.com/logins.jsp', data=payload)
    r = s.get('http://reg.163.com/Main.jsp?username=ajsdhsjdfoo')

    if '上次登录情况' not in r.content:
        logger.error(' Login Error')
        return (False, str(logger))
    logger.debug(' Login OK')

    # Step 2: 验证码
    host = get_host(post_url)
    page = s.get(post_url)
    boardId = re.findall('boardId = \"(.*?)\"', page.content)[0]
    threadId = re.findall('threadId = \"(.*?)\"', page.content)[0]

    headers = {'X-Requested-With':'XMLHttpRequest',
               'Origin':host,
               'Referer':post_url,
               'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6'
    }
    r = s.post(host + 'v2/post/replyCheck/' + boardId + '/' + threadId + '/?timestamp=1413358191224',headers=headers)
    checkCode = re.findall('\"checkCode\":\"(.*?)\",', r.content)[0]
    seccode = 0
    if checkCode == '1':
        r = s.get(host + 'v2/checkcode/codeimg?timestamp=1413358191224',
            headers={
                'Accept': config.accept_image,
                'Referer': post_url,
            })
        seccode = crack_captcha(r.content)
        logger.debug(' seccode:'+seccode)
        payload = {'code':seccode.encode('utf-8')}
        r = s.post(host + 'v2/checkcode/validate',data=payload,
            headers={
                'Origin':host,
                'Referer': post_url,
            })
        logger.debug(' '+r.content)

    # Step 3: 回复
    soup = BeautifulSoup(page.content)
    form = soup.find('form', attrs={'id': 'replyForm'})
    payload = get_datadic(form)
    payload['checkcode'] = seccode
    payload['content'] = src['content'].decode('utf8').encode('gbk')
    payload['title'] = payload['title'].decode('utf8').encode('gbk')
    r = s.post(host + 'v2/post/doReply',data=payload,
               headers={
                'Referer': post_url,
    })
    if '\"message\">' in r.content:
        logger.error(' Reply Error '+re.findall('\"message\">(.*?)</td>', r.content.decode('gbk'))[0])
        return (False, str(logger))
    logger.debug(' Reply OK')
    return (True, str(logger))
