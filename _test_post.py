# -*- coding: utf-8 -*-

import rap
import logging, logging.handlers
import sys

# Patch socket for socks proxy support.
# Comment this block when you don't use socks proxy.
# import socks
# import socket
# socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 1080)
# socket.socket = socks.socksocket


def post(post_url, src):
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    handler = logging.handlers.TimedRotatingFileHandler('log/log', 'D', 1, 0)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger('').addHandler(handler)

    # Filter requests log
    requests_log = logging.getLogger('requests')
    requests_log.setLevel(logging.ERROR)

    return rap.post(post_url, src)
if __name__ == '__main__':
    # url, log = post('http://club.kdnet.net/list.asp?boardid=2',
    #                {'username': 'ajsdhsjdfoo',
    #                 'password': '13936755635',
    #                 'subject':'多读书，可以让你觉得有许多的写作灵',
    #                 'content': '多读书，可以让你觉得有许多的写作灵感。可以让你在写 作文的方法上用的更好。多读书，可以让你觉得有许多的写作灵感。可以让你在写 作文的方法上用的更好多读书，可以让你觉得有许多的写作灵感。可以让你在写 作文的方法上用的更好多读书，可以让你觉得有许多的写作灵感。可以让你在写 作文的方法上用的更好。多读书，可以让你觉得有许多的写作灵感。可以让你在写 作文的方法上用的更好多读书，可以让你觉得有许多的写作灵感。可以让你在写 作文的方法上用的更好'})
    # print url

    import requests
    import json
    payload = {
        'website': '加国无忧论坛',
        'title': '最最常见的家常菜，这才是家的味道',
        'article': """家常菜是家庭日常制作食用的菜肴，每道菜制作过程简单，用料简单，价格适中。虽比不得餐馆中的菜肴，吃起来却是熟悉的味道，更是妈妈的特色菜肴。今天这几道菜是最常见的菜色，想要学好烹饪的童鞋，不妨拿着几道菜练手。
        尖椒土豆丝

原料：土豆、尖椒、油、盐、醋、蒜、花椒、干辣椒、小葱
1. 土豆去皮切丝，用凉水快速冲泡几次；尖椒去籽切丝、葱切末、蒜切末、干红辣椒剪成细丝。
2. 锅烧热放少许油，放入花椒粒转小火，捞出花椒粒，放入葱、蒜、红椒丝，炝锅。
3. 大火放入土豆丝煸炒几下后，放入盐、烹入醋后快炒，翻炒至土豆丝炒熟，汤汁浓稠，加入尖椒丝翻炒均匀即可出锅。
""",
        'account': 'baiduqqsougou',
        'password': 'blueshit',
    }
    r = requests.post('http://127.0.0.1:7777/post', data=payload)
    print r.content
