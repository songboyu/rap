# -*- coding: utf-8 -*-
import re
import time
import hashlib

import PyV8
import requests
from bs4 import BeautifulSoup

import utils
import config

def login_qq(sess, src):
    """ QQ登录函数

    @param sess:    requests.Session()
    @type sess:     Session

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict
    
    @return:           是否登录成功
    @rtype:            bool

    """

    # 获取验证码图片
    url = 'http://i.qq.com'
    resp = sess.get(url)
    soup = BeautifulSoup(resp.content)
    url = soup.select('#login_frame')[0]['src']
    resp = sess.get(url)
    login_sig = re.findall('login_sig:"(.*?)"', resp.content)[0]


    # 构造获取验证码图片参数
    par = {
        'appid'             : '549000912',
        'js_type'           : 1,
        'js_ver'            : 10076,
        'login_sig'         : login_sig,
        'r'                 : 0.8861454421075537,
        'regmaster'         : "",
        'u1'                : "http://qzs.qq.com/qzone/v5/loginsucc.html?para=izone",
        'uin'               : src['username']
    }
    resp = sess.get('http://check.ptlogin2.qq.com/check',params = par)
    _, vcode, uin = re.findall("'([^']+)'", resp.content)
    url = 'http://captcha.qq.com/getimage?uin='+src['username']+'&aid=549000912&cap_cd='+vcode+'&0.5720198110211641'
    resp = sess.get(url,headers={
                              'Accept': config.accept_image,
                          })
    # 获取验证码字符串
    seccode = utils.crack_captcha(resp.content)
    #构造参数
    payload = {
    'u' : src['username'],
    'verifycode' : seccode,
    'pt_vcode_v1' : 0,
    'pt_verifysession_v1':sess.s.cookies['verifysession'],
    'p' : getPwd(src['password'],uin,vcode),
    'pt_randsalt': 0,
    'u1':'http://qzs.qq.com/qzone/v5/loginsucc.html?para=izone',
    'ptredirect':0,
    'h':1,
    't':1,
    'g':1,
    'from_ui':1,
    'ptlang':2052,
    'action':'5-4-1427091605160',
    'js_ver':10116,
    'js_type':1,
    'login_sig': login_sig,
    'pt_uistyle':32,
    'aid':549000912,
    'daid':5,
    'pt_qzone_sig':1,
    '':''
    }
    for k,v in payload.items():
        print k, v
    resp = sess.get('http://ptlogin2.qq.com/login',params = payload)
    print resp.content
    return True


def to_bytes(n, length, endianess='big'):
    h = '%x' % n
    s = ('0'*(len(h) % 2) + h).zfill(length*2).decode('hex')
    return s if endianess == 'big' else s[::-1]


def getPwd(pwd,salt,vcode):
    ctxt = PyV8.JSContext()
    ctxt.enter()
    for fname in ['rsa.js', 'tea.js', 'encrypt.js']:
        with open('js/' + fname) as f:
            ctxt.eval(f.read())
    code = '$.Encryption.getEncryption("%s", "%s", "%s", false)' % (pwd, salt, vcode)
    final_pwd = ctxt.eval(code)
    print final_pwd
    return final_pwd

def post_qq_blog(post_url, src):
    """ 网易博客发帖函数

    @param post_url:   板块地址 blog.163.com
    @type post_url:    str

    @param src:        用户名，密码，回复内容，等等。
    @type src:         dict

    @return:           是否发帖成功
    @rtype:            bool

    """
    logger = utils.RAPLogger(post_url)
    sess = utils.RAPSession(src)

    # Step 1: 登录
    if not login_qq(sess, src):
        logger.error(' Login Error')
        return (False, str(logger))
    logger.info(' Login OK')
    return ('', str(logger))


def thumb_up_qq(post_url, src):
    logger = utils.RAPLogger(post_url)
    sess = utils.RAPSession(src)

    resp = sess.get(src['extra']['target_url'],
        headers={'Referer': post_url},
        params={
        'targetid': post_url.split('/')[-1],
        'callback': 'ding',
        })
    logger.info(resp.content)
    if 'Operation too frequent' in resp.content:
        logger.info('Operation too frequent')
        return(False, str(logger))
    return (True, str(logger))
