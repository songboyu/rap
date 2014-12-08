# -*- coding: utf-8 -*- 

import rap
import logging, logging.handlers
import sys

def reply(post_url, src):
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    handler = logging.handlers.TimedRotatingFileHandler('log/log', 'D', 1, 0)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger('').addHandler(handler)

    # Filter requests log
    requests_log = logging.getLogger('requests')
    requests_log.setLevel(logging.ERROR)

    return rap.reply(post_url, src)
if __name__ == '__main__':
    r, log = reply('http://www.canyu.org/n93953c10.aspx',
                   {'content': '多读书，可以让你觉得有许多的写作灵感',
                    'username':'小肖肖',
                    'password':''})