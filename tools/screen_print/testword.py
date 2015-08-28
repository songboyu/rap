#-*-coding:utf-8-*-
from screen_print_selenium import Pagescreen
if __name__=="__main__":
    #pagescreen = Pagescreen()
    #pagescreen.websearch('http://www.sina.com.cn/', [u'习近平',u'天津',u'日本']) #网页测试
    pagescreen = Pagescreen('127.0.0.1',8580)
    pagescreen.google_search(u'令计划', 'www') #google test
    pagescreen.quit()
