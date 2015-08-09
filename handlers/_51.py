# -*- coding: utf-8 -*- 

import re
from bs4 import BeautifulSoup
import urllib
import time
from utils import *

# Coding: utf8
# Captcha: not required
# Login: required
def login_51_forum(sess, src):
    """51资讯论坛登录模块

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    host = 'http://bbs.51.ca/'
    
    resp = sess.get(host + 'member.php?mod=logging&action=login')
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'name': 'login'})
    payload = get_datadic(form)
    payload['loginfield'] = 'username'
    payload['username'] = src['username']
    payload['password'] = src['password']
    payload['questionid'] = 0
    payload['answer'] = ''
    resp = sess.post(host + form['action'] + '&inajax=1', data=payload)
    # 若指定字样出现在response中，表示登录成功
    if '欢迎您回来' not in resp.content:
        return False
    return True

def reply_51_forum(post_url, src):
    
    logger = RAPLogger(post_url)
    host = get_host(post_url)
    sess = RAPSession(src)

    # 登录
    if not login_51_forum(sess, src):
        logger.error('Login Error')
        return (False, str(logger))
    logger.info('Login OK')

    resp = sess.get(post_url)
    soup = BeautifulSoup(resp.content)
    form = soup.find('form', attrs={'id': 'fastpostform'})
    payload = get_datadic(form)
    payload['message'] = src['content']
    resp = sess.post(host + form['action'] + '&inajax=1', data=payload)
    if '对不起' in resp.content:
        logger.error('Reply Error')
        return (False, str(logger))
    logger.info('Reply OK')
    return (True, str(logger))

# Coding: utf8
# Captcha: not required
# Login: required
def post_51_forum(post_url, src):
    """51资讯论坛发主贴模块

    @author: sky
    @since: 2014-12-01

    @param sess:    requests.Session()
    @type sess:     Session

    @param post_url:   帖子地址  http://bbs.51.ca/forumdisplay.php?fid=40
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否登录成功
    @rtype:            bool

    """
    logger = RAPLogger(post_url)
    sess = RAPSession(src)

    # 登录
    if not login_51_forum(sess, src):
        logger.error('Login Error')
        return ('', str(logger))
    logger.info('Login OK')

    fid = re.findall(r'fid=(\d+)', post_url)[0]
    resp = sess.get('http://bbs.51.ca/forum.php?mod=post&action=newthread&fid='+fid)
    soup = BeautifulSoup(resp.content)
    # 获得发帖form表单
    form = soup.find('form', attrs={'id': 'postform'})

    # 构造回复参数
    payload = get_datadic(form)
    payload['posttime'] = int(time.time()*1000)
    payload['wysiwyg'] = '1'
    payload['subject'] = src['subject']
    payload['message'] = src['content']

    #发送发主贴post包
    resp = sess.post('http://bbs.51.ca/forum.php?mod=post&action=newthread&fid='+fid+'&extra=&topicsubmit=yes', data=payload)
    # 若指定字样出现在response中，表示发帖成功
    if src['subject'] not in resp.content:
        logger.error('Post Error')
        return ('', str(logger))
    logger.info('Post OK')
    url = resp.url
    return (url, str(logger))
    

def get_account_info_51_forum(src):
    logger = RAPLogger('51=>' + src['username'])
    sess = RAPSession(src)

    # Step 1: 登录
    if not login_51_forum('http://bbs.51.ca/', sess, src):
        logger.error(' Login Error')
        return ({}, str(logger))
    logger.info(' Login OK')

    resp = sess.get('http://bbs.51.ca/')
    info_url = re.findall('(space-uid-\d+\.html)', resp.content)[0]
    resp = sess.get('http://bbs.51.ca/' + info_url)

    head_image = re.findall('avatar"><img src="(.*?)"', resp.content)[0]
    account_score = int(re.findall('积分: (\d+)<', resp.content)[0])
    account_class = re.findall('color="#33C">(.*?)<', resp.content)[0]
    time_register = re.findall('注册日期: (.*?)<', resp.content)[0]
    time_last_login = re.findall('上次访问: <span title="(.*?)"', resp.content)[0]
    login_count = 0
    count_post = int(re.findall('帖子: (\d+) 篇', resp.content)[0])
    # 经验 代替 回复
    count_reply = int(re.findall('经验: (\d+) 点', resp.content)[0])

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

def upload_head_51_forum(src):
    logger = RAPLogger('Upload head 51_forum=>' + src['username'])
    sess = RAPSession(src)

    # Step 1: 登录
    if not login_51_forum('http://bbs.51.ca/',sess, src):
        logger.error('Login Error')
        return ('', str(logger))
    logger.info('Login OK')

    resp = sess.get('http://bbs.51.ca/home.php?mod=spacecp&ac=avatar')
    input = urllib.unquote(re.findall(r'input=(.*?)&',resp.content)[0])
    agent = re.findall(r'agent=(.*?)&',resp.content)[0]
    head_url = re.findall(r'<td><img src="(.*?)"',resp.content)[0]
    print 'input:',input
    print 'agent:',agent

    avatar1 = binascii.hexlify(open(src['head'],'rb').read()).upper()
    avatar2 = avatar1
    avatar3 = avatar1

    params = {
        'm':'user',
        'inajax':'1',
        'a':'rectavatar',
        'appid':'1',
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
    resp = sess.post('http://uc.51.ca/index.php', data=payload, params=params)


    print resp.content
    if 'success="1"' in resp.content:
        logger.info('uploadavatar OK')
        return (head_url, str(logger))
    else:
        logger.info('uploadavatar Error')
        return ('', str(logger))

def thumb_up_51(post_url, src):
    logger = RAPLogger(post_url)
    s = RAPSession(src)

    if not login_51_forum(post_url, s, src['extra']):
        logger.error(' Login Error')
        return ('', str(logger))
    logger.info(' Login OK')
    r = s.get(post_url)
    tid = re.findall('action=printable&amp;tid=(\d+)', r.content)[0].strip('\n')
    # pid = re.findall('summary="pid(\d+)', r.content)[1].strip('\n')
    pid = src['extra']['pid']
    _hash = re.findall('name="formhash" value="(.*)"', r.content)[0].strip('\n')
    r = s.get(post_url,
        headers={'Referer':post_url,
        'Host':'bbs.51.ca',
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
        'do': 'against' if src['extra']['like']=='false' or src['extra']['like']=='False' else 'support',
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
