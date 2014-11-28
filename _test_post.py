# -*- coding: utf-8 -*-

import rap
import logging, logging.handlers
import sys

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
    r, url, log = post('http://bbs.creaders.net/life/',
                   {'username': 'shiduojiuo',
                    'password': '1qazxsw2',
                    'title':'晚上好',
                    'content': '多读书，可以让你觉得有许多的写作灵感。可以让你在写 作文的方法上用的更好。\
                    在写作的时候，我们往往可以运用一些书中的好词好句和生活哲理。让别人觉得你更富有文采，美感多读书，可以让你全身都有礼节。\
                    俗话说：第一印象最重要从你留给别人的第一印象中些书中的好词好句和生活哲理。让别人觉得你更富有文采，美感多读书，可以让你全身都有礼节。\
                    俗话说：第一印象最重要从你留给别人的第一印象中'})
    