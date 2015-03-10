# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib
import re,sys
import time
import json
import os
from utils import *
import config
import mechanize
from bs4 import BeautifulSoup
import requests
from ctypes import *

type = sys.getfilesystemencoding()


def submit_jiayi(params):
    f_user = params['username']
    f_pass = params['password']
    f_email = params['email']
    cookie = cookielib.CookieJar()
    cookie_handler = urllib2.HTTPCookieProcessor(cookie)
    hds = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36' ,
              'Host':'ieasy5.com'} 
    post_url = 'http://www.ieasy5.com/bbs/register.php'
    req = urllib2.Request(url = post_url,headers = hds)
    opener = urllib2.build_opener(cookie_handler) 
    response = opener.open(req)
    page = response.read()
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36',  
             'Referer' : 'http://ieasy5.com/bbs/register.php',
             'Origin' : 'http://ieasy5.com',
             'Connection':'keep-alive',
             'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
             'Content-Type':'application/x-www-form-urlencoded',
             'Host':'ieasy5.com'}
    checkloginname = {
        'action':'regcheck',
        'type':'regname',
        'username':f_user,
    }
    posturl = 'http://www.ieasy5.com/bbs/register.php'
    request = requests.post(posturl, data=checkloginname, headers=headers)
    text = request.content
    if 'CDATA[4]' in text:
        return '用户名已被他人注册'
    checkemail = {
        'action':'regcheck',
        'type':'regemail',
        'email':f_email,
            }
    posturl = 'http://www.ieasy5.com/bbs/register.php'
    request = requests.post(posturl, data=checkemail, headers=headers)
    text = request.content
    if 'CDATA[2]' in text:
        return '邮箱已被他人注册'
    postData = {
        'forward':"",
        'step':'2', 
        '_hexie':'641a46b8',
        'regname' : f_user,
        'regpwd' : f_pass,  
        'regpwdrepeat' : f_pass,
        'regemail' : f_email,
        'rgpermit':'1'
        }
    posturl='http://ieasy5.com/bbs/register.php?'
    postData = urllib.urlencode(postData)
    request = urllib2.Request(posturl, postData, headers)  
    response = urllib2.urlopen(request)  
    text = response.read()
    success = u'注册成功'.encode('gbk')
    if success in text:
        return '注册成功'
    else:
        return '注册失败'


def submit_51(params):
    f_user = params['username']
    f_pass = params['password']
    f_email = params['email']
    ###用cookielib模块创建一个对象，再用urlllib2模块创建一个cookie的handler
    cookie = cookielib.CookieJar()
    cookie_handler = urllib2.HTTPCookieProcessor(cookie)
    hds = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.94 Safari/537.36' ,
            'Host':'www.51.ca'} 
    post_url = 'http://www.51.ca/my/register.php?action=signup'
    req = urllib2.Request(url = post_url,headers = hds)
    opener = urllib2.build_opener(cookie_handler) 
    response = opener.open(req)#请求网页，返回句
    page = response.read()#读取并返回网页内容
    page = page.decode("UTF-8").encode(type)
    match=re.findall(r'var SESSIONHASH = \'(.*?)\'',page)
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.94 Safari/537.36',  
               'Referer' : 'http://www.51.ca/my/register.php?action=signup',
               'Origin' : 'http://www.51.ca',
               'Content-Type': 'application/x-www-form-urlencoded',
               'Cache-Control' : 'max-age=0',
               'Connection':'keep-alive',
               'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Encoding' : 'gzip, deflate',
               'Host':'www.51.ca'}
    checkloginname = {
        'loginname':f_user,
    }
    posturl = 'http://www.51.ca/ajax/ajax_checkreg.php?'+match[0]+'&op=checkloginname'
    request = requests.post(posturl, data=checkloginname, headers=headers)
    text = request.content
    text = json.loads(text)
    if len(text['errmsg']) > 0:
        return '用户名已被他人注册'
    checkemail = {
        'email':f_email,
    }
    posturl = 'http://www.51.ca/ajax/ajax_checkreg.php?'+match[0]+'&op=checkemail'
    request = requests.post(posturl, data=checkemail, headers=headers)
    text = request.content
    text = json.loads(text)
    if len(text['errmsg']) > 0:
        return '邮箱已被他人注册'
    postData = {
        's':match[0],
        'loginname':f_user,
        'username' : f_user+'25',
        'password' : f_pass,  
        'passwordconfirm' :f_pass,
        'email' : f_email,
        'emailconfirm' : f_email,
        'cookieuser':'0',
        'timezoneoffset':'-5',
        'timezoneadjust':'1',
        'agreetreaty':'1',
        'url':'http%3A%2F%2Fwww.51.ca%2Fmy%2Fusercp.php%3Fs%3D'+match[0],
        'action':'addmember'
                }
    posturl='http://www.51.ca/my/register.php'
    request = requests.post(posturl, data=postData, headers=headers)
    text = request.content
    success = u'注册成功'.encode('gb2312')
    if success in text:
        return '注册成功'
    else :
        return '注册失败'


def submit_mimi(params):
    f_user = params['username']
    f_pass = params['password']
    f_email = params['email']
    host = 'http://forum.memehk.com/member.php'
    post_url = 'http://forum.memehk.com/misc.php'
    s=requests.session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36' 
    r=s.get(host,params={
            'mod':'register'
        }, headers={'Referer': 'http://forum.memehk.com/forum.php'})
    page=r.content
    idhash = re.findall(r'id="seccodeverify_(\w*)',page)
    match=re.findall(r'name=\"formhash\" value=\"(.*?)\"',page)
    user=re.findall(r'type=\"text\" id=\"(.*?)\"',page)
    mima=re.findall(r'type=\"password\" id=\"(.*?)\"',page)
    femail=match[0].strip('\n')
    check_url = 'http://forum.memehk.com/forum.php'
    username_check = s.get(check_url,params={
        'mod':'ajax',
        'inajax':'yes',
        'infloat':'register',
        'handlekey':'register',
        'ajaxmenu':'1',
        'action':'checkusername',
        'username':f_user
        }, headers={'Referer': 'http://forum.memehk.com/member.php?mod=register'})
    if 'CDATA[succeed]' not in username_check.content:
        return '用户名已被他人注册'
    email_check = s.get(check_url,params={
        'mod':'ajax',
        'inajax':'yes',
        'infloat':'register',
        'handlekey':'register',
        'ajaxmenu':'1',
        'action':'checkemail',
        'email':f_email
        }, headers={'Referer': 'http://forum.memehk.com/member.php?mod=register'})
    if 'CDATA[succeed]' not in email_check.content:
        return '邮箱已被他人注册'
    r=s.get(post_url,params={
        'mod':'seccode',
        'update':'26349',
        'idhash':idhash[0]
        }, headers={'Referer': 'http://forum.memehk.com/member.php?mod=register'})
    seccode1 = crack_captcha(r.content)
    postData = {
    'regsubmit':'yes',
    'formhash':femail,
    'referer':'http://forum.memehk.com/',
    'activationauth':'',
    user[0]: f_user,
    mima[0]: f_pass,
    mima[1]: f_pass,
    user[1]: f_email,
    'sechash':idhash[0],
    'seccodeverify':seccode1,
    'regsubmit':'true'
    } 
    s.headers[ 'Accept']='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    s.headers[ 'Content-Type']='application/x-www-form-urlencoded'
    s.headers['Host']='forum.memehk.com'
    s.headers['Origin']='http://forum.memehk.com'
    s.headers['Referer']='http://forum.memehk.com/member.php?mod=register'
    r = s.post('http://forum.memehk.com/member.php?mod=register&inajax=1', data=urllib.urlencode(postData))
    text=r.content
    success = u'感謝您註冊'.encode('utf-8')
    if success in text:
        return '注册成功'
    else:
        return '注册失败'


def submit_tianyi(params):
    f_user = params['username']
    f_pass = params['password']
    f_email = params['email']
    host = 'http://www.wolfax.com/member.php?mod=register'
    post_url = 'http://www.wolfax.com/misc.php'
    s=requests.session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36' 
    r=s.get(host,params={
            'mod':'register'
        }, headers={'Referer': 'http://www.wolfax.com/member.php?mod=register'})
    page=r.content
    idhash = re.findall(r'secqaa_(\w*)',page)
    idhash2=re.findall(r'seccode_(\w*)',page)
    match=re.findall(r'name=\"formhash\" value=\"(.*?)\"',page)
    user=re.findall(r'type=\"text\" id=\"(.*?)\"',page)
    mima=re.findall(r'type=\"password\" id=\"(.*?)\"',page)
    femail=match[0].strip('\n')
    check_url = 'http://www.wolfax.com/forum.php'
    username_check = s.get(check_url,params={
        'mod':'ajax',
        'inajax':'yes',
        'infloat':'register',
        'handlekey':'register',
        'ajaxmenu':'1',
        'action':'checkusername',
        'username':f_user
        }, headers={'Referer': 'http://www.wolfax.com/member.php?mod=register'})
    if 'CDATA[succeed]' not in username_check.content:
        return '用户名已被他人注册'
    email_check = s.get(check_url,params={
        'mod':'ajax',
        'inajax':'yes',
        'infloat':'register',
        'handlekey':'register',
        'ajaxmenu':'1',
        'action':'checkemail',
        'email':f_email
        }, headers={'Referer': 'http://www.wolfax.com/member.php?mod=register'})
    if 'CDATA[succeed]' not in email_check.content:
        return '邮箱已被他人注册'
    r=s.get(post_url,params={
            'mod': 'secqaa',
            'action': 'update',
            'idhash': idhash[0],
        }, headers={'Referer': 'http://www.wolfax.com/member.php?mod=register'})
    page=r.content
    a, op, b = re.findall("'(\d+) (.) (\d+)", page)[0]
    seccode = int(a) + int(b) if op == '+' else int(a) - int(b)
    r=s.get(post_url,params={
        'mod':'seccode',
        'update':'26126',
        'idhash':idhash2[0]
        }, headers={'Referer': 'http://www.wolfax.com/member.php?mod=register'})
    seccode1= crack_captcha(r.content)
    postData = {
    'regsubmit':'yes',
    'formhash':femail,
    'referer':'http://www.wolfax.com/',
    'activationauth':'',
    user[0]: f_user,
    mima[0]: f_pass,
    mima[1]: f_pass,
    user[1]: f_email,
    'invitecode':'',
    'gender':'1',
    'secqaahash':idhash[0],
    'secanswer':seccode,
    'seccodehash':idhash2[0],
    'seccodemodid':'member::register',
    'seccodeverify':seccode1,
    'regsubmit':'true'
    } 
    s.headers[ 'Accept']='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    s.headers[ 'Content-Type']='application/x-www-form-urlencoded'
    s.headers['Host']='www.wolfax.com'
    s.headers['Origin']='http://www.wolfax.com'
    s.headers['Referer']='http://www.wolfax.com/member.php?mod=register'
    r = s.post('http://www.wolfax.com/member.php?mod=register&inajax=1', data=urllib.urlencode(postData))
    text=r.content
    success = u'感谢您注册'.encode('utf-8')
    if success in text:
        return '注册成功'
    else:
        return '注册失败'


def submit_wenxuecheng(params):
    f_user = params['username']
    f_pass = params['password']
    f_email = params['email']
    post_url = 'http://www.wenxuecity.com/members/passport.php?act=register' 
    img_url = 'http://www.wenxuecity.com/members/script/sessCode.php'
    br = mechanize.Browser()
    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)
    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    url = 'http://www.wenxuecity.com/members/passport.php'
    s=requests.session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.94 Safari/537.36' 
    r=s.get(url,params={
            'act':'checkusername',
            'username':f_user,
        }, headers={'Referer': 'http://www.wenxuecity.com/members/passport.php?act=register'})
    page=r.content
    if u'已经存在'.encode('utf-8') in page:
        return '用户名已被他人注册'
    agent_header = ('User-agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36')
        # Step 1: Load post page.
    br.addheaders = [agent_header]
    br.open(post_url)
        # Step 2: Retrieve captcha.
    br.addheaders = [
        ('Host','www.wenxuecity.com'),
        agent_header, 
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
            ('Accept-Encoding','gzip,deflate,sdch'),
            ('Accept-Language','zh-CN,zh;q=0.8'),
            ('Cache-Control','max-age=0'),
            ('Proxy-Connection','keep-alive'),
            ('Referer', post_url)
        ]
    r = br.open_novisit(img_url)
    seccode = crack_captcha(r.read())
    br.select_form(name="register")
    br["username"] =f_user
    br["password"]=f_pass
    br["confirm"]=f_pass
    br["email"]=f_email
    br["email_confirm"]=f_email
    br["zipcode"]="555555"
    br["private_key"]=str(seccode)
    res = br.submit()
    if len(br.response().read()) < 2500:
        return '注册成功'
    else:
        return '邮箱已被他人注册'
