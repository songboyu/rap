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
    requests_log = logging.getLogger('requesocks')
    requests_log.setLevel(logging.ERROR)

    return rap.reply(post_url, src)
if __name__ == '__main__':

    # test reply
    # http://global.dwnews.com/news/2015-01-14/59629846.html ok
    # http://blog.dwnews.com/post-814621.html ok

    # http://www.mirrorbooks.com/MIB/news/news.aspx?ID=N000072075 ok

    # http://www.ieasy5.com/htm/chinanews/2015-01-15/19431.html ok
    # http://www.ieasy5.com/bbs/read.php?tid=2293 ok

    # http://www.aboluowang.com/pinlun%2Fcontent_55-500496-1 ok
    # http://bbs.aboluowang.com/forum.php?mod=viewthread&tid=885275&extra=page%3D1 ok

    # http://bbs.wolfax.com/t-27930-1-1.html ok

    # http://forum.vanhi.com/forum.php?mod=viewthread&tid=230891 ok

    # http://www.secretchina.com/news/15/01/14/565493.html ok

    # http://news.creaders.net/china/2015/01/14/1478134.html ok
    # http://bbs.creaders.net/poem/bbsviewer.php?btrd_id=3771239&btrd_trd_id=1024007 ok

    # http://www.wenxuecity.com/news/2015/01/14/3950227.html ok
    # http://blog.wenxuecity.com/myblog/66438/201501/16246.html ok
    # http://bbs.wenxuecity.com/znjy/2741902.html ok

    # http://forum.memehk.com/forum.php?mod=viewthread&tid=82005&extra=page%3D1 ok

    # http://bbs.51.ca/thread-615406-1-1.html ok

    # http://bbs.eulam.com/ShowPost.asp?ThreadID=171870 ok

    # boxun fail

    # http://boxun.com/news/gb/china/2015/01/201501142221.shtml fail

    r, log = reply('http://boxun.com/forum/201501/boxun2013/18895.shtml',
                    {'content': '墙里墙外 男默女泪',
                     'username': 'shiduojiuo',
                     'password': '1qazxsw2',
                     'proxies': {'http': 'socks5://127.0.0.1:1080', 'https': 'socks5://127.0.0.1:1080'},
                    })
