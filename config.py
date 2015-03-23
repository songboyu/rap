# -*- coding: utf-8 -*- 

# Http config
http_timeout = 30
max_redirects = 3
max_try = 5

# Default headers
user_agent = 'Mozilla/5\.0 (Windows NT 6\.3; WOW64) AppleWebKit/537\.36 (KHTML, like Gecko) Chrome/37\.0\.2062\.124 Safari/537\.36'
accept_image = 'image/webp,*/*;q=0\.8'

# Captcha interface
# chaoren
chaoren_softwareid = '6942'
chaoren_username = 'shiduojiuo'
chaoren_password = '1qazxsw2'

# URL dispatch
dispatch_rule = {
    # # IN
    # r'163\.com/\d+/\d+/\d+/\w+\.html': ('163_news', 'IN', '网易', 'http://news.163.com/'),
    # r'163\.com/blog/static/\d+': ('163_blog', 'IN', '网易', 'http://blog.163.com/'),
    # r'163\.com/bbs/\w+/\d+\.html': ('163_bbs', 'IN', '网易', 'http://bbs.163.com/'),

    # r'kdnet\.net/dispbbs\.asp': ('kdnet', 'IN', '凯迪', 'http://club.kdnet.net/'),

    # r'sina\.com\.cn/(\w+/)*\d\d\d\d-\d\d-\d\d/\w+\.shtml': ('sina_news', 'IN', '新浪', 'http://news.sina.com.cn/'),
    # r'sina\.com\.cn/((\w+/)*thread-\d+-\d-\d\.html|viewthread\.php)': ('sina_club', 'IN', '新浪', 'http://bbs.sina.com.cn/'),

    # r'sohu\.com/\d{8}/\w+\.shtml': ('sohu_news', 'IN', '搜狐', 'http://news.sohu.com/'),

    # # OUT
    # r'dwnews\.com/news/\d\d\d\d-\d\d-\d\d/\d+\.html': ('dwnews_news', 'OUT', '多维', 'http://www.dwnews.com/'),
    # r'dwnews\.com/post-\d+\.html': ('dwnews_blog', 'OUT', '多维', 'http://blog.dwnews.com/'),

    'csdn\.net': ('csdn_blog', 'IN'),

    # By HSS
    # unitedtimes
    'unitedtimes\.com\.au/':('unitedtimes','OUT'),
    # inmediahk
    'www\.inmediahk\.net/':('inmediahk','OUT'),
    # kdnet
    'club\.kdnet\.net/': ('kdnet', 'IN'),
    # sciencenet
    'bbs\.sciencenet\.cn/': ('sciencenet', 'IN'),
    # 163
    'blog\.163\.com/': ('163_blog', 'IN'),
    '(view|news)\.163\.com/[0-9]': ('163_news', 'IN'),
    'bbs.*\.163\.com/bbs/': ('163_bbs', 'IN'),
    # sina
    '(forum|club).*\.sina\.com\.cn': ('sina_club', 'IN'),
    '^http://[^(c|f)].*\.sina\.com\.cn/': ('sina_news', 'IN'),
    'blog\.sina\.com\.cn/': ('sina_blog', 'IN'),
    # sohu
    'news\.sohu\.com/':('sohu_news','IN'),
    # enewstree
    'enewstree\.com/discuz/forum':('enewstree_forum','OUT'),
    # 1dpw
    'bbs\.1dpw\.com':('1dpw_forum','OUT'),
    # iask
    'forum\.iask\.ca':('iask_forum','OUT'),
    # mirrorbooks
    'www\.(mirrorbooks|mingjingnews)\.com/MIB/blog': ('mirrorbooks_blog', 'OUT'),
    # penchinese
    'www\.penchinese\.org/blog':('penchinese_blog','OUT'),

    # By kerry
    # backchina
    'www\.backchina\.com/forum': ('backchina_forum', 'OUT'),
    # powerapple
    'bbs\.powerapple\.com': ('powerapple_forum', 'OUT'),
    # wailaike
    'www\.wailaike\.net': ('wailaike_forum', 'OUT'),

    # By sky
    # powerapple
    'news\.powerapple\.com': ('powerapple_news', 'OUT'),
    # creaders
    'bbs\.creaders\.net': ('creaders_forum', 'OUT'),
    # wenxuecity
    'blog\.wenxuecity\.com': ('wenxuecity_blog', 'OUT'),
    # myca168 
    'www\.myca168\.com': ('myca168_forum', 'OUT'),
    # onmoon
    'www\.onmoon\.com':('onmoon_news','OUT'),
    # canyu
    'www\.canyu\.org/':('canyu','OUT'),
    # cenews
    'www\.cenews\.eu/':('cenews','OUT'),

    # By sniper
    # dwnews
    'dwnews\.com/news': ('dwnews_news', 'OUT'),
    'blog\.dwnews\.com': ('dwnews_blog', 'OUT'),
    # mirrorbooks
    'www\.(mirrorbooks|mingjingnews)\.com/MIB/news': ('mirrorbooks_news', 'OUT'),
    # ieasy5
    'ieasy5\.com/htm': ('ieasy5_news', 'OUT'),
    'ieasy5\.com/bbs': ('ieasy5_forum', 'OUT'),
    # aboluowang
    '(bbs|space)\.aboluowang\.com': ('aboluowang_forum', 'OUT'),
    '(www|tw)\.aboluowang\.com': ('aboluowang_news', 'OUT'),
    # wolfax
    '(wolfax\.com/forum|bbs\.wolfax\.com)': ('wolfax_forum', 'OUT'),
    'wolfax\.com/home': ('wolfax_blog', 'OUT'),
    # vanhi
    'forum\.vanhi\.com': ('vanhi_forum', 'OUT') ,
    # secretchina
    'www\.secretchina\.com': ('secretchina_news', 'OUT'),
    'm\.secretchina\.com': ('m_secretchina_news', 'OUT'),
    # creaders
    'news\.creaders\.net': ('creaders_news', 'OUT'),

    # By hm
    # wenxuecity
    'bbs\.wenxuecity\.com': ('wenxuecity_forum', 'OUT'),
    'wenxuecity\.com/news': ('wenxuecity_news', 'OUT'),
    # memehk
    'forum\.memehk\.com': ('memehk_forum', 'OUT'),
    # 51
    'bbs\.51\.ca': ('51_forum', 'OUT'),
    # eulam
    'bbs\.eulam\.com': ('eulam_forum', 'OUT'),
    # boxun
    'boxun\.com/forum': ('boxun_forum', 'OUT'),

    # CasperJS
    'boxun\.com/news': ('disqus', 'OUT'),
    'blog\.boxun\.com': ('disqus', 'OUT'),
}

website_rule = {
    '凯迪社区': ('kdnet', 'http://club.kdnet.net/list.asp?boardid=2'),
    '加国华人网论坛': ('1dpw_forum', 'http://bbs.1dpw.com/forum-71-1.html'),
    '加国无忧论坛': ('51_forum', 'http://bbs.51.ca/forum-40-1.html'),
    '倍可亲论坛': ('backchina_forum', 'http://www.backchina.com/forum/37/index-1.html'),
    '万维论坛': ('creaders_forum', 'http://bbs.creaders.net/life/'),
    '多维博客': ('dwnews_blog', 'http://blog.dwnews.com/'),
    '消息树论坛': ('enewstree_forum', 'http://enewstree.com/discuz/forum.php?mod=forumdisplay&fid=47'),
    '加拿大家园论坛': ('iask_forum', 'http://forum.iask.ca/forums/%E6%B8%A9%E5%93%A5%E5%8D%8E.14/'),
    '加拿大加易论坛': ('ieasy5_forum', 'http://ieasy5.com/bbs/thread.php?fid=3'),
    '明镜博客': ('mirrorbooks_blog', 'http://www.mirrorbooks.com/MIB/blog/main.aspx'),
    '天涯信息论坛': ('myca168_forum', 'http://www.myca168.com/bbs/index/thread/id/9'),
    '文学城博客': ('wenxuecity_blog', 'http://blog.wenxuecity.com'),
    '外来客论坛': ('wailaike_forum', 'http://www.wailaike.net/group_post?gid=1'),
    '天易论坛': ('wolfax_forum', 'http://bbs.wolfax.com/f-42-1.html'),
    '温哥华巅峰论坛': ('vanhi_forum', 'http://forum.vanhi.com/forum-38-1.html'),
    '謎米香港论坛': ('memehk_forum', 'http://forum.memehk.com/forum.php?mod=forumdisplay&fid=60'),
    '阿波罗论坛': ('aboluowang_forum', 'http://bbs.aboluowang.com/forum.php?mod=forumdisplay&fid=3'),
}

praise_rule = {
    'comment\.news\.163\.com': '163',
    'quan\.sohu\.com': 'sohu',
    'coral\.qq\.com': 'qq',
    'blog\.dwnews\.com': 'dwnews',
    'bbs\.51\.ca': '51',
    '(bbs|space)\.aboluowang\.com': 'aboluowang',
}

account_rule = {
    '无忧':'51',
    '加易':'jiayi',
    '谜米':'mimi',
    '天易':'tianyi',
    '文学城':'wenxuecheng',
}

account_status_map = {
    '网易': '163_bbs',
    '凯迪': 'kdnet',
    '文学城': 'wenxuecity_blog',
    '无忧': '51_forum',
    '加易': 'ieasy5_forum',
    '天易': 'wolfax_forum',
    '温哥华': 'vanhi_forum',
    '谜米': 'memehk_forum',
    '消息树': 'enewstree_forum',
    '超级苹果': 'powerapple_forum',
    '外来客': 'wailaike_forum',
    '新浪': 'sina_club',
    '欧浪': 'eulam_forum',
    '加国华人网': '1dpw_forum',
    '多维': 'dwnews_blog',
    '阿波罗': 'aboluowang_forum',
    '倍可亲': 'backchina_forum',
}