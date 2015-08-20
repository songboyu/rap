# -*- coding: utf-8 -*- 

import requests, re, random, logging
from bs4 import BeautifulSoup
from hashlib import md5
import urllib
import time
import binascii

import config
from utils import *


def login_aboluowang(sess, src):
    host = 'http://bbs.aboluowang.com/'
    resp = sess.get(host)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id': 'lsform'})

    payload = get_datadic(form)
    payload['username'] = src['username']
    payload['password'] = md5(src['password']).hexdigest()

    resp = sess.post(host + form['action'], data=payload)
    soup = BeautifulSoup(resp.content)
    tag = soup.find('div', attrs={'id': 'messagetext'})
    if tag:
        return False
    return True


# Coding: utf8
# Captcha: arithmetic
# Login: required
def reply_aboluowang_forum(post_url, src):
    if src['TTL'] == 0:
        raise RAPMaxTryException('captcha')
    logger = RAPLogger(post_url)

    host = get_host(post_url)
    sess = RAPSession(src)

    # Step 1: Login
    if not login_aboluowang(sess, src):
        logger.error('Login Error')
        return (False, str(logger))
    logger.info('Login OK')

    # Step 2: Load post page
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'fastpostform'})

    # Step 3: Retrieve captcha question and crack
    resp = sess.get(host + 'misc.php',
                    params={
                        'mod': 'secqaa',
                        'action': 'update',
                        'idhash': hidden_value(form, 'sechash'),
                        'inajax': 1,
                        'ajaxtarget': 'secqaa_' + hidden_value(form, 'sechash'),
                    },
                    headers={'Referer': post_url})

    # Crack the silly captcha question
    # Server responses are as follows: 
    # <root><![CDATA[输入下面问题的答案<br />七加五是多少？]]></root>
    # <root><![CDATA[输入下面问题的答案<br />七加三是多少？]]></root>
    # ...
    chinese_numbers = [u'零', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九']
    formula = resp.content.decode('utf8')
    plus_index = formula.find(u'加')
    a = chinese_numbers.index(formula[plus_index - 1]) 
    b = chinese_numbers.index(formula[plus_index + 1]) 
    seccode = a + b
    logger.info('%d + %d = %d' % (a, b, seccode))

    # Verify the captcha question ACTIVELY.
    resp = sess.get('http://bbs.aboluowang.com/misc.php',
                    params={
                        'mod': 'secqaa',
                        'action': 'check',
                        'idhash': hidden_value(form, 'sechash'),
                        'inajax': 1,
                        'secverify': seccode,
                    },
                    headers={'Referer': post_url})

    # Step 4: Submit and check
    payload = get_datadic(form)
    if 'subject' in src:
        payload['subject'] = src['subject']
    payload['message'] = src['content']
    payload['secanswer'] = seccode

    resp = sess.post(host + form['action'], data=payload)
    soup = BeautifulSoup(resp.content)
    tag = soup.find('div', attrs={'id': 'messagetext'})
    if tag:
        logger.error('Reply Error: ' + tag.find('p').text)
        # Captcha cracking is absolutely right, unless the schema has changed
        # It's not necessary to retry for captcha error
        # But it is necessary now...
        if u'验证问答' in tag.find('p').text:
            src['TTL'] -= 1
            return reply_aboluowang_forum(post_url, src)
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))


# Coding: utf8
# Captcha: required
# Login: not required
def reply_aboluowang_news(post_url, src):
    if src['TTL'] == 0:
        raise RAPMaxTryException('captcha')
    logger = RAPLogger(post_url)

    host = get_host(post_url)
    sess = RAPSession(src)

    # If this is news page, then go to comment page.
    if 'pinlun' not in post_url:
        resp = sess.get(post_url)
        post_url = host + re.findall('(/pinlun[^"]*)', resp.content)[0]

    # Load comment page.
    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form')

    # Crack captcha.
    resp = sess.get(host + '/api.php?op=checkcode&code_len=4&font_size=20&width=130&height=50&font_color=&background=&0.23309023911133409',
        headers={
            'Accept': config.accept_image,
            'Referer': post_url,
        })
    seccode = crack_captcha(resp.content)

    # Reply
    payload = get_datadic(form)
    payload['content'] = src['content']
    payload['code'] = seccode
    resp = sess.post(form['action'], data=payload)
    if '操作成功' not in resp.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))


def post_aboluowang_forum(post_url, src):
    if src['TTL'] == 0:
        raise RAPMaxTryException('captcha')
    logger = RAPLogger(post_url)

    host = get_host(post_url)
    sess = RAPSession(src)

    # Step 1: Login
    if not login_aboluowang(sess, src):
        logger.error('Login Error')
        return ('', str(logger))
    logger.info('Login OK')

    fid = re.findall(r'fid=(\d+)', post_url)[0]
    # # Step 2: Load post page
    resp = sess.get('http://bbs.aboluowang.com/forum.php?mod=post&action=newthread&fid='+fid+'&infloat=yes&handlekey=newthread&inajax=1&ajaxtarget=fwin_content_newthread')
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id':'postform'})
    #
    # # Step 3: Retrieve captcha question and crack
    # resp = sess.get(host + 'misc.php',
    #                 params={
    #                     'mod': 'secqaa',
    #                     'action': 'update',
    #                     'idhash': hidden_value(form, 'sechash'),
    #                     'inajax': 1,
    #                     'ajaxtarget': 'secqaa_' + hidden_value(form, 'sechash'),
    #                 },
    #                 headers={'Referer': post_url})
    
    # # Crack the silly captcha question
    # # Server responses are as follows:
    # # <root><![CDATA[输入下面问题的答案<br />七加五是多少？]]></root>
    # # <root><![CDATA[输入下面问题的答案<br />七加三是多少？]]></root>
    # # ...
    # chinese_numbers = [u'零', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九']
    # formula = resp.content.decode('utf8')
    # plus_index = formula.find(u'加')
    # a = chinese_numbers.index(formula[plus_index - 1])
    # b = chinese_numbers.index(formula[plus_index + 1])
    # seccode = a + b
    # logger.info('%d + %d = %d' % (a, b, seccode))
    
    # # Verify the captcha question ACTIVELY.
    # resp = sess.get('http://bbs.aboluowang.com/misc.php',
    #                 params={
    #                     'mod': 'secqaa',
    #                     'action': 'check',
    #                     'idhash': hidden_value(form, 'sechash'),
    #                     'inajax': 1,
    #                     'secverify': seccode,
    #                 },
    #                 headers={'Referer': post_url})
    #
    # # Step 4: Submit and check
    payload = get_datadic(form)
    payload['subject'] = src['subject']
    payload['message'] = src['content']
    # payload['secanswer'] = seccode

    resp = sess.post(host + form['action'], data=payload)
    # print_to_file(resp.content)
    # soup = BeautifulSoup(resp.content)
    # tag = soup.find('div', attrs={'id': 'messagetext'})
    # if tag:
    #     logger.error('Post Error: ' + tag.find('p').text)
    #     # Captcha cracking is absolutely right, unless the schema has changed
    #     # It's not necessary to retry for captcha error
    #     # But it is necessary now...
    #     if u'验证问答' in tag.find('p').text:
    #         src['TTL'] -= 1
    #         return post_aboluowang_forum(post_url, src)
    #     return ('', str(logger))
    if src['subject'] not in resp.content:
        logger.info('Post Error')
        return ('', str(logger))
    logger.info('Post OK')
    return (resp.url, str(logger))

def get_account_info_aboluowang_forum(src):
    """ 阿波罗账户信息获取函数

    @param src:        用户名，密码
    @type src:         dict

    @return:           账户信息
    @rtype:            dict
    """
    logger = RAPLogger(src['username'])
    sess = RAPSession(src)

    # Step 1: 登录
    if not login_aboluowang(sess, src):
        logger.error(' Login Error')
        return ({}, str(logger))
    logger.info(' Login OK')

    resp = sess.get('http://bbs.aboluowang.com/home.php?mod=space&do=profile')

    soup = BeautifulSoup(resp.content)
    head_image = soup.select('a.avtm img')[0]['src']

    account_score = re.findall(r'<li><em>积分</em>(.*?)</li>', resp.content)[0]
    account_class = re.findall(r'ac=usergroup.*>(.*?)</a>', resp.content)[0]

    time_register = re.findall(r'<li><em>注册时间</em>(.*?)</li>', resp.content)[0]
    time_last_login = re.findall(r'<li><em>上次活动时间</em>(.*?)</li>', resp.content)[0]

    login_count = ''

    count_post = re.findall(r'主题数 (.*?)<', resp.content)[0]
    count_reply = re.findall(r'回帖数 (.*?)<', resp.content)[0]

    account_info = {
        #########################################
        # 用户名
        'username':src['username'],
        # 密码
        'password':src['password'],
        # 头像图片
        'head_image':head_image,
        #########################################
        # 积分
        'account_score':account_score,
        # 等级
        'account_class':account_class,
        #########################################
        # 注册时间
        'time_register':time_register,
        # 最近登录时间
        'time_last_login':time_last_login,
        # 登录次数
        'login_count':login_count,
        #########################################
        # 主帖数
        'count_post':count_post,
        # 回复数
        'count_reply':count_reply
        #########################################
    }
    logger.info('Get account info OK')
    return (account_info, str(logger))


def upload_head_aboluowang_forum(src):
    logger = RAPLogger('Upload head aboluowang_forum=>' + src['username'])
    sess = RAPSession(src)

    # Step 1: 登录
    if not login_aboluowang(sess, src):
        logger.error('Login Error')
        return ('', str(logger))
    logger.info('Login OK')

    resp = sess.get('http://bbs.aboluowang.com/home.php?mod=spacecp&ac=avatar')
    input = urllib.unquote(re.findall(r'input=(.*?)&',resp.content)[0])
    agent = re.findall(r'agent=(.*?)&',resp.content)[0]
    print 'input:',input
    print 'agent:',agent

    avatar1 = binascii.hexlify(open(src['head'],'rb').read()).upper()
    avatar2 = avatar1
    avatar3 = avatar1

    params = {
        'm':'user',
        'inajax':'1',
        'a':'rectavatar',
        'appid':'3',
        'input':input,
        'agent':agent,
        'avatartype':'virtual'
    }
    payload = {
        'avatar1':avatar1,
        'avatar2':avatar2,
        'avatar3':avatar3,
        'urlReaderTS':str(time.time()*1000)
    }
    resp = sess.post('http://uc.ablwang.com/index.php', data=payload, params=params)


    print resp.content
    if 'success="1"' in resp.content:
        logger.info('uploadavatar OK')
        return ('', str(logger))
    else:
        logger.info('uploadavatar Error')
        return ('', str(logger))

def thumb_up_aboluowang(post_url, src):
    logger = RAPLogger(post_url)
    s = RAPSession(src)

    if not login_aboluowang(s, src['extra']):
        logger.error('Login Error')
        return (False, str(logger))
    logger.info('Login OK')

    r = s.get(post_url)
    tid = re.findall('action=printable&amp;tid=(\d+)', r.content)[0].strip('\n')
    # pid = re.findall('summary="pid(\d+)', r.content)[1].strip('\n')
    pid = src['extra']['pid']
    _hash = re.findall('name="formhash" value="(.*)"', r.content)[0].strip('\n')
    url = 'http://bbs.aboluowang.com/forum.php'
    r = s.get(post_url,
        headers={'Referer':post_url,
        'Host':'bbs.aboluowang.com',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest',
        'Accept':'*/*',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Connection':'keep-alive',
        },
        params={
        'mod':'misc',
        'action':'postreview',
        'do':'against' if src['extra']['like']=='false' or src['extra']['like']=='False' else 'support',
        'tid':tid,
        'pid':pid,
        'hash':_hash,
        })
    if '您已经对此回帖投过票了' in r.content:
        logger.error('您已经对此回帖投过票了')
        return (False, str(logger))
    if '投票成功' not in r.content:
        logger.error('Thumb Up Error')
        return (False, str(logger))
    logger.info('Thumb Up OK')
    return (True, str(logger))
