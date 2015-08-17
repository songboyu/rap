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
    url, log = post('http://bbs.powerapple.com/forum.php?mod=forumdisplay&fid=50',
                   {'username': 'wefefxd',
                    'password': 'qqq123',
                    'subject':'澳媒：美军在南海强硬没用 只会让中国更果决',
                    'content': """澳大利亚《世纪报》8月14日文章，原题：美国的强硬政策解决不了南海挑战 如今，越来越多官员和分析家敦促华盛顿采取更强硬行动，应对北京在南海的战略力量潜滋暗长。但强硬的美国政策不会让中国退缩，反而会损害华盛顿的战略地位。
　　理论上讲，美国海军进行航行自由行动，将表明华盛顿对阻止北京利用造岛限制外国军队活动是当真的。美国防规划者还希望，强力展示军力将遏阻北京推进对这些岛屿的军事化。遗憾的是，这种做法可能适得其反。此类行为将被北京视为军事挑衅，虽然华盛顿并无此意。这种情况下，中国几乎肯定做出反应，迫使美国摊牌。中国人不会满足美国的要求，反而会加大使用无线电警告，驱赶外国海军和海岸警卫队。更糟的是，中国可能开始派出军舰和飞机，拦截美国或其他地区国家的军队。
　　那时，美国该如何应对？是示弱容忍中国，抑或发布更强硬的最后通牒，冒着引发冲突的危险？不论怎样做，华盛顿都将处于一种画出红线、但不升级危机就无法执行的尴尬境地。


　　采取强硬行动，也会推高中国高层忽视不起的国内压力。在大多数中国人看来，南海岛屿不仅是主权领土，也是国家尊严及结束“屈辱世纪”努力的象征。美军舰凌驾中国海域的画面，必将激起要坚决反应的民族主义呼声。这还会助长中国军方的强硬派，他们如今已在呼吁北京建立南海防空识别区了。
　　那美国撮合设立一套行为准则，不考虑中国因素，这种做法如何？看似讲得通。鉴于北京一再拖延与东盟签署此类协议，或许是时候不理睬中国了。希望这样会使北京受排斥或受声誉损失，从而被迫谈判或加入。但这种做法可能产生反效果。华盛顿若另起炉灶，将强化中国人对美国干涉的看法。单是这一条就足以令北京变成更好斗和不合作的外交伙伴。就像菲律宾决定把中国告上国际法庭，愈加坚定北京的态度一样。
　　而且，一些谨慎的国家如印尼、马来西亚甚至新加坡是否会接受不仅排除中国，又缺少政治上最重要的东盟共识的协议，这是个大问号。大多数东盟国家可能害怕遭到北京的经济惩罚。
　　所以，美国采取强硬政策只会助长北京的胆量或激起地区紧张，以此法解决南海挑战将适得其反。(作者阿什利·汤申德，乔恒译)"""})
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
