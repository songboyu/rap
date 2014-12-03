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
    # By HSS
    # unitedtimes
    'unitedtimes\.com\.au/':('unitedtimes','OUT'),
    # inmediahk
    'www\.inmediahk\.net/':('inmediahk','OUT'),
    # kdnet
    'club\.kdnet\.net/': ('kdnet', 'IN'),
    # 163
    'blog\.163\.com/': ('163_blog', 'IN'),
    '(view|news)\.163\.com/[0-9]': ('163_news', 'IN'),
    'bbs.*\.163\.com/bbs/': ('163_bbs', 'IN'),
    # sina
    '(forum|club).*\.sina\.com\.cn': ('sina_club', 'IN'),
    '^http://[^(c|f)].*\.sina\.com\.cn/': ('sina_news', 'IN'),
    # sohu
    'news\.sohu\.com/':('sohu_news','IN'),
    'enewstree\.com/discuz/forum':('enewstree_forum','OUT'),
    # 1dpw
    'bbs\.1dpw\.com':('1dpw_forum','OUT'),

    # By kerry
    # backchina
    'www\.backchina\.com/forum': ('backchina_forum', 'OUT'),
    # powerapple
    'bbs\.powerapple\.com': ('powerapple_forum', 'OUT'),

    # By sky
    # powerapple
    'news\.powerapple\.com': ('powerapple_news', 'OUT'),
    # creaders
    'bbs\.creaders\.net': ('creaders_forum', 'OUT'),
    # wenxuecity
    'blog\.wenxuecity\.com': ('wenxuecity_blog', 'OUT'),

    # By sniper
    # dwnews
    'dwnews\.com/news': ('dwnews_news', 'OUT'),
    'blog\.dwnews\.com': ('dwnews_blog', 'OUT'),
    # mirrorbooks
    'www\.(mirrorbooks|mingjingnews)\.com/MIB/news': ('mirrorbooks_news', 'OUT'),
    'www\.(mirrorbooks|mingjingnews)\.com/MIB/blog': ('mirrorbooks_blog', 'OUT'),
    # ieasy5
    'ieasy5\.com/htm': ('ieasy5_news', 'OUT'),
    'ieasy5\.com/bbs': ('ieasy5_forum', 'OUT'),
    # aboluowang
    'bbs\.aboluowang\.com': ('aboluowang_forum', 'OUT'),
    'space\.aboluowang\.com': ('aboluowang_forum', 'OUT'),
    'www\.aboluowang\.com': ('aboluowang_news', 'OUT'),
    'tw\.aboluowang\.com': ('aboluowang_news', 'OUT'),
    # wolfax
    'bbs\.wolfax\.com': ('wolfax_forum', 'OUT'),
    # vanhi
    'forum\.vanhi\.com': ('vanhi_forum', 'OUT') ,
    # secretchina
    'www\.secretchina\.com': ('secretchina_news', 'OUT'),
    # creaders
    'news\.creaders\.net': ('creaders_news', 'OUT'),

    # By hm
    # wenxuecity
    'bbs\.wenxuecity\.com': ('wenxuecity_forum', 'OUT'),
    'wenxuecity\.com/news': ('wenxuecity_news', 'OUT'),
    'wenxuecity\.com/myblog': ('wenxuecity_blog', 'OUT'),
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