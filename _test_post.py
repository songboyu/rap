# -*- coding: utf-8 -*-

import rap
import logging, logging.handlers
import sys

# Patch socket for socks proxy support.
# Comment this block when you don't use socks proxy.
import socks
import socket
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 1080)
socket.socket = socks.socksocket


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
    url, log = post('http://club.kdnet.net/list.asp?boardid=2',
                   {'username': 'ajsdhsjdfoo',
                    'password': '13936755635',
                    'subject':'多读书，可以让你觉得有许多的写作灵',
                    'content': '多读书，可以让你觉得有许多的写作灵感。可以让你在写 作文的方法上用的更好。多读书，可以让你觉得有许多的写作灵感。可以让你在写 作文的方法上用的更好多读书，可以让你觉得有许多的写作灵感。可以让你在写 作文的方法上用的更好多读书，可以让你觉得有许多的写作灵感。可以让你在写 作文的方法上用的更好。多读书，可以让你觉得有许多的写作灵感。可以让你在写 作文的方法上用的更好多读书，可以让你觉得有许多的写作灵感。可以让你在写 作文的方法上用的更好'})
    print url