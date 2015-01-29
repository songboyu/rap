# -*- coding: utf-8 -*-
"""超级苹果回复模块

@author: kerry & sky
@since: 2014-10-25
@summary: 超级苹果论坛，超级苹果新闻
"""

from bs4 import BeautifulSoup
from hashlib import md5
from utils import get_datadic
from utils import get_host
from utils import RAPSession
from utils import RAPLogger

# Coding: utf8
# Captcha: arithmetic
# Login: required
def reply_powerapple_forum(post_url, src):
    """超级苹果论坛回复模块
    @author: kerry
    @since: 2014-10-25

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   帖子地址
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    # Returnable logger
    logger = RAPLogger(post_url)

    host = get_host(post_url)
    sess = RAPSession(src)

    # Step 1: Login
    #登录页面
    resp = sess.get(
        host + '/member.php?mod=logging&action=login')
    #获取登录页面content的HTML
    soup = BeautifulSoup(resp.content)
    #查找与{'name': 'login'}匹配的form标签
    form = soup.find('form', attrs={'name': 'login'})
    #将form标签中的form属性内容存入payload中
    payload = get_datadic(form)

     #将src['username']内容，src['password']加密后内容存入payload中
    payload['username'] = src['username']
    payload['password'] = md5(src['password']).hexdigest()

    #发送post包
    resp = sess.post(host + form['action'], data=payload)
    soup = BeautifulSoup(resp.content)

    #判断登录后页面是否含有用户字段，若存在则证明登录成功，否则失败
    if src['username'] in resp.content:
        logger.info('Login OK')
    else:
        logger.error(
            'Login Error: Username Or Password error , please try again !')
        return (False, str(logger))

    # Step 2: Load post page
    # 获取所需发帖页面，查找与{'id':'fastpostform'}匹配的form标签
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'fastpostform'})

    # Step 3: Submit
    # 回复内容
    payload = get_datadic(form)
    if 'subject' in src:
        payload['subject'] = src['subject']
    payload['message'] = src['content']

    #发送post包
    resp = sess.post(host + form['action'], data=payload)
    #获取回帖页面content的HTML
    soup = BeautifulSoup(resp.content)

    #判断回帖后页面是否含有回帖内容，若存在则证明回帖成功，否则失败
    if src['content'] in resp.content:
        logger.info('Reply OK')
    else:
        logger.error('Login Error: Reply Error, please try again !')
        return (False, str(logger))
    return (True, str(logger))


# Coding: utf8
# Captcha: required
# Login: not required
def reply_powerapple_news(post_url, src):
    """超级苹果新闻回帖模块
    @author: sky
    @since: 2014-11-11

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   帖子地址
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    if src['TTL'] == 0:
        raise RAPMaxTryException('captcha')
    logger = RAPLogger(post_url)

    host = get_host(post_url)
    sess = RAPSession(src)


    # Step 1: 获取回帖页面
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'new_comment'})
    # Step 2: 验证码
    # 获取验证码图片
    resp = sess.get(host + 'captcha',
    headers={
        'Accept': config.accept_image,
        'Referer': post_url
    },
    params={'type': '', 'time': time.time()*1000})
    # 获取验证码字符串              
    seccode = crack_captcha(resp.content)
    logger.info(' seccode:' + seccode)

    # Step 3: 提交回帖
    # 回复内容
    name = soup.find('input', attrs={'name': 'authenticity_token'})
    name1 = name.attrs['value']
    payload = {}
    payload['utf8'] = '%E2%9C%93'
    payload['comment[reply_to_id]:'] = ''
    payload['comment[content]'] = src['content']
    payload['captcha'] = seccode
    payload['authenticity_token'] = name1
    #发送post包
    resp = sess.post(host + form['action'], data=payload)
    #再次请求原网页，查看是否已经有回帖内容
    resp = sess.get(post_url)
    #判断回帖后页面是否含有回帖内容，若存在则证明回帖成功，否则失败
    if src['content'] in resp.content:
        logger.info('Reply OK')
    else:
        logger.error('Login Error: Reply Error, please try again !')
        return (False, str(logger))
    return (True, str(logger))
