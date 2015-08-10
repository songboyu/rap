# -*- coding: utf-8 -*-
"""澳洲新足迹模块

@author: HSS
@since: 2015-8-11
@summary: 澳洲新足迹
"""
import re
from bs4 import BeautifulSoup
from utils import *
import config
import gifextract

def login_oursteps(sess, src):
    """ 澳洲新足迹登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
 # Step 1: Login
    #登录页面
    host = 'https://www.oursteps.com.au/bbs/'
    resp = sess.get(host + '/member.php?mod=logging&action=login')
    #获取登录页面content的HTML
    soup = BeautifulSoup(resp.content)
    #查找与{'name': 'login'}匹配的form标签
    form = soup.find('form', attrs={'name': 'login'})
    #将form标签中的form属性内容存入payload中
    payload = get_datadic(form)

    #将src['username']内容，src['password']加密后内容存入payload中
    payload['username'] = src['username']
    payload['password'] = src['password']
    payload['questionid'] = 0
    payload['loginfield'] = 'username'

    #发送post包
    resp = sess.post(host + form['action']+'&inajax=1', data=payload)
    # with open('attach/debug.html', 'w') as f:
    #     f.write(resp.content)
    #判断登录后页面是否含有用户字段，若存在则证明登录成功，否则失败
    if src['username'] in resp.content:
        return True
    return False

def post_oursteps_forum(post_url, src):
    """澳洲新足迹论坛主贴模块
    @author: HSS
    @since: 2015-8-10

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   板块地址  https://www.oursteps.com.au/bbs/forum.php?mod=forumdisplay&fid=160
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    logger = RAPLogger(post_url)
    sess = RAPSession(src)
    host = 'https://www.oursteps.com.au/bbs/'
    # Step 1: 登录
    if not login_oursteps(sess, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.info(' Login OK')

    fid = re.findall(r'fid=(\d+)', post_url)[0]
    resp = sess.get(host + '/forum.php?mod=post&action=newthread&fid='+fid)
    soup = BeautifulSoup(resp.content)

    form = soup.find('form', attrs={'id': 'postform'})
    payload = get_datadic(form)
    payload['subject'] = src['subject']
    payload['message'] = src['content']
    sechash = soup.find('input', attrs={'name': 'sechash'})['value']
    resp = sess.get(host + '/misc.php?mod=seccode&action=update&idhash='+sechash+'&inajax=1&ajaxtarget=seccode_'+sechash)

    resp = sess.get(host + re.findall(r'src="(.*?)"', resp.content)[0],
                    headers={'Accept': config.accept_image,
                             'Referer': host + '/forum.php?mod=post&action=newthread&fid='+fid})
    result = gifextract.processImage(resp.content, 'attach/result.png')
    seccode = crack_captcha(result)
    print seccode
    payload['seccodeverify'] = seccode

    resp = sess.get(host + '/misc.php?mod=secqaa&action=update&idhash='+sechash+'&inajax=1&ajaxtarget=secqaa_'+sechash,
                    headers={'Referer': host + '/forum.php?mod=post&action=newthread&fid='+fid})

    if '5 加 1 减 2 等于' in resp.content:
        payload['secanswer'] = '4'
    elif '中国英文最后一个字母是' in resp.content:
        payload['secanswer'] = 'o'
    elif '100 的1后面有多少个0' in resp.content:
        payload['secanswer'] = '2'
    elif '10 等于多少个 5' in resp.content:
        payload['secanswer'] = '2'
    print resp.content,payload['secanswer']

    #发送post包
    resp = sess.post(host + form['action'], data=payload)
    # with open('attach/debug.html', 'w') as f:
    #     f.write(resp.content)
    if '主题已发布' in resp.content:
        logger.info('Post OK')
    else:
        logger.error('Post Error')
        return ('', str(logger))
    url = host + re.findall(r'<a href="(.*?)">如果你的浏览器没', resp.content)[0]
    return (url, str(logger))

