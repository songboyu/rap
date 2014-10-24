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
    'club\.kdnet\.net/': 'kdnet',
    'blog\.163\.com/': '163_blog',
    'news\.163\.com/[0-9]': '163_news',
    'bbs.*\.163\.com/bbs/': '163_bbs',
    '(forum|club).*\.sina\.com\.cn': 'sina_club',
    '^http://[^(c|f)].*\.sina\.com\.cn/':'sina_news',

    # By kerry
    # backchina
    'www\.backchina\.com': 'backchina_forum',
    # powerapple
    'bbs\.powerapple\.com': 'powerapple_forum',

    # By sniper
    # dwnews
    'dwnews\.com/news': 'dwnews_news',
    'blog\.dwnews\.com': 'dwnews_blog',
    # mirrorbooks
    'www\.mirrorbooks\.com': 'mirrorbooks_news',
    'www\.mingjingnews\.com': 'mirrorbooks_news',
    # ieasy5
    'ieasy5\.com/htm': 'ieasy5_news',
    'ieasy5\.com/bbs': 'ieasy5_forum',
    # aboluowang
    'bbs\.aboluowang\.com': 'aboluowang_forum',
    'space\.aboluowang\.com': 'aboluowang_forum',
    'www\.aboluowang\.com': 'aboluowang_news',
    'tw\.aboluowang\.com': 'aboluowang_news',
    # wolfax
    'bbs\.wolfax\.com': 'wolfax_forum',
    # vanhi
    'forum\.vanhi\.com': 'vanhi_forum',
    # secretchina
    'www\.secretchina\.com': 'secretchina_news',
    # creaders
    'news\.creaders\.net': 'creaders_news',

    # By hm
    # wenxuecity
    'bbs\.wenxuecity\.com': 'wenxuecity_forum',
    'wenxuecity\.com/news': 'wenxuecity_news',
    'wenxuecity\.com/myblog': 'wenxuecity_blog',
    # memehk
    'forum\.memehk\.com': 'memehk_forum',
    # 51
    'bbs\.51\.ca': '51_forum',
    # eulam
    'bbs\.eulam\.com': 'eulam_forum',
    # boxun
    'boxun\.com/forum': 'boxun_forum',

    # CasperJS
    'boxun\.com/news': 'disqus',
    'blog\.boxun\.com': 'disqus',
}