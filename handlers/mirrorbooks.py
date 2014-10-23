# -*- coding: utf-8 -*- 

import requests, re, random, logging
from bs4 import BeautifulSoup

import config
from utils import *

# Coding: utf8
# Captcha: required
# Login: not required
def reply_mirrorbooks_news(post_url, src):
    if src['TTL'] == 0:
        raise RAPMaxTryException('captcha')
    logger = RAPLogger(post_url)

    # This handler works for 'www.mirrorbooks.com' and 'www.mingjingnews.com'
    # 'mingjingnews' is a synonym for 'mirrorbooks', but the reply is always unsuccessful(Captcha error while I don't know why).
    # So I just redirect 'mingjingnews' to 'mirrorbooks' if necessary.
    if 'mingjingnews' in post_url:
        post_url = post_url.replace('mingjingnews', 'mirrorbooks')

    s = RAPSession(src)
    r = s.get(post_url)
    payload = {
        'ScriptManager1': 'UpdatePanel2|btn_reply_send',
        'NSSrc$src': 'rbl1',
        '__VIEWSTATE': re.findall('id="__VIEWSTATE" value="(.*?)"', r.content)[0],
        '__EVENTVALIDATION': re.findall('id="__EVENTVALIDATION" value="(.*?)"', r.content)[0],
        '__ASYNCPOST': 'true',
        'btn_reply_send': '發表',
        'tbx_CKEditor': src['content'],
    }

    r = s.get('http://www.mirrorbooks.com/MIB/UserControls/imgcode.aspx',
        headers={
            'Accept': config.accept_image,
            'Referer': post_url,
        })
    seccode = crack_captcha(r.content)

    payload['ImageCode$tbx_Code'] = seccode
    r = s.post(post_url, data=payload)
    if '發表成功' not in r.content:
        logger.error('Reply Error')
        if '驗証碼' in r.content:
            src['TTL'] -= 1
            return reply_mirrorbooks_news2(post_url, src)
        return (False, str(logger))
    logger.debug('Reply OK')
    return (True, str(logger))
