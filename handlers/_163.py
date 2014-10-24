# -*- coding: utf-8 -*-
"""网易回复模块

* Author: songboyu
* Modify: 2014-10-20
* Coding: gbk
* Contain：网易博客、网易新闻、网易论坛

"""
import re
import time
import urllib

from bs4 import BeautifulSoup

import config
import utils

# 网易网页编码
CODING = 'gbk'

def login_163(session, src):
    """网易登录函数

    :param session:    Request.session
    :param src:        回复参数(username, password, content etc.)
    :return:           success? True:False

    """
    # 登录页面
    login_page = 'http://reg.163.com/'
    response = session.get(login_page)
    soup = BeautifulSoup(response.content)
    # 获取登录form
    form = soup.find('form', attrs={'id': 'fLogin'})
    # 构造登录参数
    payload = utils.get_datadic(form)
    payload['username'] = src['username']
    payload['password'] = src['password']
    # 发送登录post包
    response = session.post(login_page + 'logins.jsp', data=payload)
    # 获取页面跳转地址
    redirects = re.findall(r'location.replace\(\"(.*?)\"\)',
                           response.content)
    # 获取登录结果
    response = session.get(redirects[0])
    # 若指定字样出现在response中，表示登录成功
    if '上次登录情况' not in response.content:
        return False
    return True

# name:     网易博客
# Feature:  blog.163.com
# Captcha:  required
# Login:    required
def reply_163_blog(post_url, src):
    """网易博客回复函数

    :param post_url:   博客地址
    :param src:        {username, password, content etc.}
    :return:           success? True:False

    """
    logger = utils.RAPLogger(post_url)
    session = utils.RAPSession(src)

    ## Step 1: 登录
    if not login_163(session, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.debug(' Login OK')

    ## Step 2: 验证码
    response = session.get(post_url)
    parent_id = re.findall(r'userId:(.*?),', response.content)[0]
    # 获取验证码图片
    response = session.get('http://api.blog.163.com/cap/captcha.jpgx?'
                          'parentId=' + parent_id,
                          headers={
                              'Accept': config.accept_image,
                              'Referer': post_url,
                              })
    # 获取验证码字符串
    seccode = utils.crack_captcha(response.content)
    logger.debug(' seccode:'+seccode)

    ## Step 3: 提交回复
    response = session.get(post_url)
    soup = BeautifulSoup(response.content)
    meta = soup.find('meta', attrs={'name': 'author'})
    # 从页面中获取各项参数
    page_id = re.findall('id:\'(.*?)\'', response.content)[0]
    parent_id = re.findall('parentId=(.*?)&', response.content)[0]
    author_0 = urllib.quote(meta.attrs['content'].split(',')[0].encode(CODING))
    author_1 = urllib.quote(meta.attrs['content'].split(',')[1].encode(CODING))
    content = urllib.quote(src['content']+'<wbr>')
    # 构造回复参数
    payload = 'callCount=1\n'+\
             'scriptSessionId=${scriptSessionId}187\n'+\
             'c0-scriptName=BlogBeanNew\n'+\
             'c0-methodName=addBlogComment\n'+\
             'c0-id=0\n'+\
             'c0-e1=string:'+page_id+'\n'+\
             'c0-e2=number:'+parent_id+'\n'+\
             'c0-e3=string:\n'+\
             'c0-e4=string:'''+content+'\n'+\
             'c0-e5=string:'''+src['username']+'\n'+\
             'c0-e6=string:\n'+\
             'c0-e7=number:-1\n'+\
             'c0-e8=number:-1\n'+\
             'c0-e9=number:'''+parent_id+'\n'+\
             'c0-e10=string:'''+author_0+'\n'+\
             'c0-e11=string:'''+author_1+'\n'+\
             'c0-e12=boolean:true\n'+\
             'c0-param0=Object_Object:' \
             '{blogId:reference:c0-e1,' \
             'blogUserId:reference:c0-e2,' \
             'blogTitle:reference:c0-e3,' \
             'content:reference:c0-e4,' \
             'publisherNickname:reference:c0-e5,' \
             'publisherEmail:reference:c0-e6,' \
             'mainComId:reference:c0-e7,' \
             'replyComId:reference:c0-e8,' \
             'replyToUserId:reference:c0-e9,' \
             'replyToUserName:reference:c0-e10,' \
             'replyToUserNick:reference:c0-e11,' \
             'synchMiniBlog:reference:c0-e12}\n'+\
             'c0-param1=string:'''+seccode+'\n'+\
             'c0-param2=boolean:false\n'+\
             'batchId=118652'
    # 请求头设置
    headers = {'Content-Type':'text/plain',
               'Origin':'http://api.blog.163.com',
               'Referer':'http://api.blog.163.com/crossdomain.html?t=20100205',
               'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6'}
    # 发送回复post包
    response = session.post('http://api.blog.163.com/xinluduwu/dwr/'
                           'call/plaincall/BlogBeanNew.addBlogComment.dwr',
                           data=payload, headers=headers)
    # 若指定字样出现在response中，表示回复成功
    if '_remoteHandleCallback' not in response.content:
        logger.debug(response.content)
        logger.error(' Reply Error')
        return (False, str(logger))
    logger.debug(' Reply OK')
    return (True, str(logger))

# name:     网易新闻
# Feature:  news.163.com/[0-9]
# Captcha:  required
# Login:    required
def reply_163_news(post_url, src):
    """网易新闻回复函数

    :param post_url:   新闻地址
    :param src:        {username, password, content etc.}
    :return:           success? True:False

    """
    logger = utils.RAPLogger(post_url)
    session = utils.RAPSession(src)

    ## Step 1: 登录
    if not login_163(session, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.debug(' Login OK')


    ## Step 2: 验证码
    response = session.get(post_url)
    # 获取各项参数
    board_id = re.findall('boardId = \"(.*?)\"', response.content)[0]
    thread_id = re.findall('threadId = \"(.*?)\"', response.content)[0]
    comments_url = "http://comment.news.163.com/" + \
                  board_id + "/" + thread_id + ".html"
    # 构造请求头
    headers = {'X-Requested-With':'XMLHttpRequest',
               'Origin':'http://comment.news.163.com',
               'Referer':comments_url,
               'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6'}
    # 询问是否需要验证码
    response = session.get('http://comment.news.163.com/reply/needvalidate.jsp?'
                          'time=1413303328581', headers=headers)
    # 询问结果
    need_validate = re.findall('needValidate:([0-9])', response.content)[0]

    seccode = ''
    validate_sucess = False
    post_times = 0
    # 如果需要验证码
    if need_validate == '1':
        # 询问验证码是否正确，如果不正确再次发送
        while not validate_sucess \
                and post_times < src['TTl']:
            # 限制最大发送次数
            post_times = post_times + 1
            # 获取验证图片
            response = session.get('http://comment.news.163.com/reply/'
                                  'auth/validatecode.jsp?rnd=',
                                  headers={
                                      'Accept': config.accept_image,
                                      'Referer': comments_url,
                                      })
            # 获取验证码字符串
            seccode = utils.crack_captcha(response.content)
            logger.debug(' seccode:'+seccode)
            # 询问验证码是否正确
            response = session.get('http://comment.news.163.com/reply/'
                                  'isValidateCodeValid.jsp?'
                                  'validateCode='+seccode,
                                  headers={
                                      'Referer': comments_url,
                                      })
            logger.debug(response.content)
            validate_sucess = 'true' in response.content

    ## Step 3: 回复
    # 构造回复参数
    payload = {
        'board':board_id,
        'quote':'',
        'threadid':thread_id,
        'hidename':False,
        'username':src['username'],
        'body':src['content'],
        'isTinyBlogSyn':1,
        'flag':'',
        'validateCode':seccode,
    }
    # 发送回复post包
    response = session.post('http://comment.news.163.com/reply/dopost.jsp',
                           data=payload, headers=headers)
    # 若指定字样出现在response中，表示回复成功
    if '网易首页' not in response.content:
        logger.error(' Reply Error')
        return (False, str(logger))
    logger.debug(' Reply OK')
    return (True, str(logger))

# name:     网易论坛
# Feature:  bbs.*.163.com/bbs/
# Captcha:  required
# Login:    required
def reply_163_bbs(post_url, src):
    """网易论坛回复函数

    :param post_url:   帖子地址
    :param src:        {username, password, content etc.}
    :return:           success? True:False

    """
    logger = utils.RAPLogger(post_url)
    session = utils.RAPSession(src)

    # Step 1: 登录
    if not login_163(session, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.debug(' Login OK')

    # Step 2: 验证码
    host = utils.get_host(post_url)
    logger.debug(host)
    page = session.get(post_url)
    # 获取各项参数
    board_id = re.findall('boardId = \"(.*?)\"', page.content)[0]
    thread_id = re.findall('threadId = \"(.*?)\"', page.content)[0]
    # 当前时间戳
    timestamp = str(time.time())
    # 询问是否需要验证码
    response = session.post(host + 'v2/post/replyCheck/' + board_id +
                           '/' +thread_id + '/?timestamp=' + timestamp,
                           headers={
                               'X-Requested-With':'XMLHttpRequest',
                               'Origin':host,
                               'Referer':post_url,
                               'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6'
                           })
    # 询问结果
    check_code = re.findall('\"checkCode\":\"(.*?)\",', response.content)[0]
    logger.debug(check_code)

    seccode = ''
    validate_sucess = False
    post_times = 0
    # 如果需要验证码
    if check_code == '1':
        # 询问验证码是否正确，如果不正确再次发送
        while not validate_sucess \
                and post_times < src['TTl']:
            # 限制最大发送次数
            post_times = post_times + 1
            # 获取验证码图片
            response = session.get(host + 'v2/checkcode/codeimg?timestamp='
                                  + timestamp,
                                  headers={
                                      'Accept': config.accept_image,
                                      'Referer': post_url,
                                      })
            # 获取验证码字符串
            seccode = utils.crack_captcha(response.content)
            logger.debug(' seccode:'+seccode)
            # 发送验证码，询问是否正确
            payload = {'code':seccode.encode('utf-8')}
            response = session.post(host + 'v2/checkcode/validate', data=payload,
                                   headers={
                                       'Origin':host,
                                       'Referer': post_url,
                                       })
            logger.debug(response.content)
            validate_sucess = '"code":1' in response.content

    ## Step 3: 回复
    # 构造回复参数
    payload = {
        'checkcode':seccode,
        'content':src['content'].decode('utf8').encode(CODING),
        'title':re.findall('<title>(.*?)</title>', page.content)[0],
        'boardId':board_id,
        'threadId':thread_id
    }
    # 发送回复post包
    response = session.post(host + 'v2/post/doReply', data=payload,
                           headers={
                               'Referer': post_url,
                               })
    # 若指定字样出现在response中，表示回复成功
    if '\"message\">' in response.content:
        logger.error(' Reply Error '+
                     re.findall('\"message\">(.*?)</td>',
                                response.content.decode(CODING))[0])
        return (False, str(logger))
    logger.debug(' Reply OK')
    return (True, str(logger))
