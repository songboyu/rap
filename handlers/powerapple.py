# -*- coding: utf-8 -*-
'''
posting for powerapple
'''
from bs4 import BeautifulSoup
from hashlib import md5
from handlers.utils import get_datadic
from handlers.utils import get_host
from handlers.utils import RAPSession
from handlers.utils import RAPLogger

# Coding: utf8
# Captcha: arithmetic
# Login: required
def reply_powerapple_forum(post_url, src):
    '''
        posting for backchina
        parameters :
                    post_url : 所需发帖论坛url
                    src : 回复参数
        return ：
                返回是否登录成功，以及是否回帖成功
        exception:
                  无
    '''
    # Returnable logger
    logger = RAPLogger(post_url)

    host = get_host(post_url)
    session = RAPSession(src)
    print session

    # Step 1: Login
    #登录页面
    respond = session.get(
        host + '/member.php?mod=logging&action=login')
    #获取登录页面content的HTML
    soup = BeautifulSoup(respond.content)
    #查找与{'name': 'login'}匹配的form标签
    form = soup.find('form', attrs={'name': 'login'})
    #将form标签中的form属性内容存入payload中
    payload = get_datadic(form)

     #将src['username']内容，src['password']加密后内容存入payload中
    payload['username'] = src['username']
    payload['password'] = md5(src['password']).hexdigest()

    #发送post包
    respond = session.post(host + form['action'], data=payload)
    soup = BeautifulSoup(respond.content)

    #判断登录后页面是否含有用户字段，若存在则证明登录成功，否则失败
    if src['username'] in respond.content:
        logger.debug('Login OK')
    else:
        logger.error(
            'Login Error: Username Or Password error , please try again !')
        return (False, str(logger))

    # Step 2: Load post page
    # 获取所需发帖页面，查找与{'id':'fastpostform'}匹配的form标签
    respond = session.get(post_url)
    soup = BeautifulSoup(respond.content)
    form = soup.find('form', attrs={'id':'fastpostform'})

    # Step 3: Submit
    # 回复内容
    payload = get_datadic(form)
    if 'subject' in src:
        payload['subject'] = src['subject']
    payload['message'] = src['content']

    #发送post包
    respond = session.post(host + form['action'], data=payload)
    #获取回帖页面content的HTML
    soup = BeautifulSoup(respond.content)

    #判断回帖后页面是否含有回帖内容，若存在则证明回帖成功，否则失败
    if src['content'] in respond.content:
        logger.debug('Reply OK')
    else:
        logger.error('Login Error: Reply Error, please try again !')
        return (False, str(logger))
    return (True, str(logger))



