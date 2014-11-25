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
    #r, log = reply('http://view.163.com/14/1030/09/A9Q0FD8J00012Q9L.html',
    #               {'username': 'ajsdhsjdfoo@163.com',
    #               'password': '13936755635',
    #                'content': '大家中午好'})
    r, log = reply('http://www.backchina.com/forum/20141122/info-1245817-1-1.html',
                   {'username': 'like_test',
                    'password': 'Like12345',
                    'content': '看起来很不错的样子'})