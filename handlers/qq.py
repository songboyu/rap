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
        'js_ver'            : 10116,
        'login_sig'         : login_sig,
        'r'                 : 0.8861454421075537,
        'regmaster'         : "",
        'pt_tea'            : "1",
        'u1'                : "http://qzs.qq.com/qzone/v5/loginsucc.html?para=izone",
        'uin'               : src['username']
    }
    resp = sess.get('http://check.ptlogin2.qq.com/check',params = par)
    print resp.content
    _, vcode, uin,_,_ = re.findall(r'\'(.*?)\'', resp.content)
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
    'p' : getPwd(src['password'],uin,seccode),
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
    # for k,v in payload.items():
    #     print k, v
    resp = sess.get('http://ptlogin2.qq.com/login',params = payload)
    print resp.content
    if '登录成功' in resp.content:
        return True
    return False

def getPwd(pwd,salt,vcode):
    ctxt = PyV8.JSContext()
    ctxt.enter()
    for fname in ['rsa.js', 'tea.js', 'encrypt.js']:
        with open('js/' + fname) as f:
            ctxt.eval(f.read())
    code = '$.Encryption.getEncryption("%s", "%s", "%s", false)' % (pwd, salt, vcode)
    final_pwd = ctxt.eval(code)
    # print final_pwd
    return final_pwd

def post_qq_blog(post_url, src):
    """ QQ空间发帖函数

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

    payload = {
        'qzreferrer':'http://edu.qzs.qq.com/qzone/newblog/v5/editor.html#opener=refererurl&source=1&refererurl=http%3A%2F%2Fedu.qzs.qq.com%2Fqzone%2Fapp%2Fblog%2Fv6%2Fbloglist.html%23nojump%3D1%26page%3D1%26catalog%3Dlist',
        'cate':'个人日记',
        'title':src['subject'],
        'html':'<div class="blog_details_20120222"><div>&nbsp;'+src['content']+'<br></div></div>',
        'source':1,
        'blogType':0,
        'lp_type':0,
        'lp_flag':0,
        'lp_id':81177,
        'lp_style':16843520,
        'autograph':1,
        'topFlag':0,
        'feeds':1,
        'tweetFlag':0,
        'rightType':1,
        'uin':src['username'],
        'hostUin':src['username'],
        'iNotice':1,
        'inCharset':'utf-8',
        'outCharset':'utf-8',
        'format':'fs',
        'ref':'qzone',
        'json':1,
        'g_tk':getToken(sess)
    }
    print getToken(sess)
    resp = sess.post('http://b1.edu.qzone.qq.com/cgi-bin/blognew/add_blog?g_tk='+str(getToken(sess)), data=payload)
    if '发表成功' not in resp.content:
        logger.error(' Post Error')
        return ('', str(logger))
    blogId = re.findall(r'"blogid":(\d+)',resp.content)[0]
    logger.error(' Post OK')
    return ('http://user.qzone.qq.com/'+src['username']+'/2/'+blogId, str(logger))

def getToken(sess):
    b = sess.s.cookies['skey'] or sess.s.cookies['rv2']
    a = 5381
    for c in range(0,len(b)):
        a += (a << 5) + ord(b[c])
    return a & 2147483647

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
