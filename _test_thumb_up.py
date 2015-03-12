
import sys
import json

import requests
import handlers

import logging, logging.handlers

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
handler = logging.handlers.TimedRotatingFileHandler('log/log', 'D', 1, 0)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logging.getLogger('').addHandler(handler)

if __name__ == '__main__':
    
    # handlers.thumb_up_163(
    #     'http://comment.news.163.com/news3_bbs/AK6B6TVH00014JB6.html',
    #     {
    #         'extra': {'target_url': 'http://comment.news.163.com/reply/upvote/news3_bbs/AK6B6TVH00014JB6_AK6G0ON2'},
    #         'TTL': 5,
    #         'proxies': '',
    #     }
    # )

    # handlers.thumb_up_sohu(
    #     'http://quan.sohu.com/pinglun/cyqemw6s1/409482113',
    #     {
    #         'extra': {'comment_id': '629659051', 'topic_id': '507216872'},
    #         'TTL': 5,
    #         'proxies': '',
    #     }
    # )

    # handlers.thumb_up_qq(
    #     'http://coral.qq.com/1114873711',
    #     {
    #         'extra': {'target_url': 'http://w.coral.qq.com/article/comment/up/to/5980251539306531055'},
    #         'TTL': 5,
    #         'proxies': '',
    #     }
    # )

    # payload = {
    #     'url': 'http://coral.qq.com/1114873711',
    #     'extra': "{'target_url': 'http://w.coral.qq.com/article/comment/up/to/5980251539306531055'}",
    #     # 'proxy_ip': '192.168.60.15',
    #     # 'proxy_port': '808',
    #     # 'proxy_type': 'http'
    # }

    payload = {
        'url': 'http://blog.dwnews.com/post-820332.html',
        'extra': "{'like':'true'}"
    }
    

    # payload = {
    #     'url': 'http://bbs.51.ca/thread-627266-1-1.html',
    #     'extra': "{'like':'true', 'pid': '3030614','username':'baiduqqsougou','password':'blueshit'}"
    # }

    # payload = {
    #     'url': 'http://bbs.aboluowang.com/forum.php?mod=viewthread&tid=944219&extra=page%3D1',
    #     'extra': "{'pid': '1170643','username':'kong0014','password':'h65352475'}",
    # }

    r = requests.post('http://127.0.0.1:7777/praise', data=payload)
    print r.content