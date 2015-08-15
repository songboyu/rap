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
    url, log = post('http://enewstree.com/discuz/forum.php?mod=forumdisplay&fid=59',
                   {'username': 'banana',
                    'password': 'qazxsw',
                    'subject':'媒体称孙杨宣布退赛前曾与巴西女运动员起争执',
                    'content': """新华社喀山8月10日体育专电 熟悉游泳的人都知道，泳池中人与人难免有一些肢体接触，喀山游泳世锦赛由于参赛选手众多，比赛池和热身池总是仿佛“下饺子”，热闹非凡。运动员之间有点小碰撞本来很正常，但是这事到了孙杨身上，就格外引人关注。而实际上，无论是对孙杨，对中国游泳队，还是巴西游泳队来说，这都是“小事一桩”。

据孙杨本人回忆，事情的经过是这样的：9日上午，已经收获世锦赛2金1银的孙杨来到泳池进行训练，准备晚上即将举行的男子1500米自由泳决赛。由于连日比赛，孙杨感到身体很不舒服，他下水后遇到了戴脚蹼的巴西运动员奥利维拉，被脚蹼踢到了。正常情况下，泳池训练不允许戴脚蹼，尤其是在已经拥挤不堪的喀山世锦赛热身池，但是这确实是一种训练打腿的手段，所以运动员之间彼此理解。

被打到了的孙杨忍不住抓住巴西女运动员的脚蹼，让她停下来，试图告诉她不要戴脚蹼。可能在语言交流中产生误会，脾气火爆的巴西姑娘生气地用脚蹼又扫了一下孙杨。孙杨也生气了，又试图沟通，结果被继续误会，两人在水中比划了起来，孙杨让对方摘掉脚蹼。据说，当时其他岸上的巴西选手也加入了声援队友的行列中。

巴西泳协新闻官艾莉安娜·阿尔维斯透露，她在递交给国际泳联的报告中写道“9日上午，孙杨和奥利维拉在热身池里发生了‘接触’，但不是打架。”阿尔维斯一再强调：“这是小事情，泳池中很常见，大家不要误会。”


在9日晚孙杨举行的新闻发布会上，他解释了由于心脏不适，他直到最后一刻才宣布退赛。因为按照规定，如果正常情况下选择退赛，应该在预赛和半决赛后半小时提出申请，预留出足够的时间给递补的第九名选手。孙杨之后也简单回应了上午与巴西女运动员的纠纷。

“这是一件小事情，泳池中经常发生，”说话时孙杨脸色苍白。

中国游泳队科研组组长陆一帆表示：“我们和巴西泳协的关系很好，已经就这件事沟通过了，我们也道歉了。大家都理解，这是个小插曲，泳池里天天都发生，运动员之间的小磕碰。”

有些媒体将这件事与孙杨退赛联系在一起，对此陆一帆说：“孙杨退赛是晚上的事情，原因是赛前身体不适，和上午在泳池中的事情没有关系。”"""})
    print url
    
#     import requests
#     import json
#     payload = {
#         'website': '加国无忧论坛',
#         'title': '最最常见的家常菜，这才是家的味道',
#         'article': """家常菜是家庭日常制作食用的菜肴，每道菜制作过程简单，用料简单，价格适中。虽比不得餐馆中的菜肴，吃起来却是熟悉的味道，更是妈妈的特色菜肴。今天这几道菜是最常见的菜色，想要学好烹饪的童鞋，不妨拿着几道菜练手。
#         尖椒土豆丝

# 原料：土豆、尖椒、油、盐、醋、蒜、花椒、干辣椒、小葱
# 1. 土豆去皮切丝，用凉水快速冲泡几次；尖椒去籽切丝、葱切末、蒜切末、干红辣椒剪成细丝。
# 2. 锅烧热放少许油，放入花椒粒转小火，捞出花椒粒，放入葱、蒜、红椒丝，炝锅。
# 3. 大火放入土豆丝煸炒几下后，放入盐、烹入醋后快炒，翻炒至土豆丝炒熟，汤汁浓稠，加入尖椒丝翻炒均匀即可出锅。
# """,
#         'account': 'baiduqqsougou',
#         'password': 'blueshit',
#     }
#     r = requests.post('http://127.0.0.1:7777/post', data=payload)
#     print r.content
