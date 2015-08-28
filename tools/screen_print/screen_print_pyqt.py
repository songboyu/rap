#-*-coding:utf-8-*-
'''
Created on 2015年8月24日

@author: yx
要求3个参数，网址 保存名 字符串数组
'''
import sys
import os.path
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *

reload(sys)
sys.setdefaultencoding('utf-8')
 
class Pagescreen(QWidget):
    def __init__(self,url,savename,input=[]):
        QWidget.__init__(self)
        self.url = url
        self.savename = savename
        self.webpage = None
        self.input = input
        fd = QFile("red.js")
        if fd.open(QIODevice.ReadOnly | QFile.Text):
            self.red = QTextStream(fd).readAll()
            fd.close()
        else:
            self.red = ''
        fd = QFile("jquery-2.1.1.js")
        if fd.open(QIODevice.ReadOnly | QFile.Text):
            self.jquery = QTextStream(fd).readAll()
            fd.close()
        else:
            self.jquery = '' 
 
    def shot(self):#载入网页
        web = QWebView(self)
        web.load(QUrl(self.url)) 
        self.webpage = web.page() 
        self.connect(web,SIGNAL("loadFinished(bool)"), self.save)#事件连接

    def input_str(self):
        for line in self.input:
            search_str = line.strip()

            code = u'redblock("'+search_str+'");'
            #code = u'var s="'+self.search_str+'";var reg=new RegExp("("+s+")","g");var str=document.body.innerHTML;var newstr=str.replace(reg,\'<span style="background:yellow">$1</span>\');document.body.innerHTML=newstr;null'
            self.webpage.mainFrame().evaluateJavaScript(code)
 
    def save(self,finished):
        if finished:
            # self.webpage.mainFrame().evaluateJavaScript(self.jquery)
            # self.webpage.mainFrame().evaluateJavaScript(self.red)
            # self.input_str()
            size = self.webpage.mainFrame().contentsSize()
            self.webpage.setViewportSize(QSize(size.width(),size.height()))
            img = QImage(size, QImage.Format_ARGB32)

            painter = QPainter(img)#绘图
            self.webpage.mainFrame().render(painter)
            
            painter.end()
            img.save(self.savename)
        else:
            print "载入错误，有可能网址错误！输入网址为 " + self.url
        self.close()
 
def url_check(url):
   import re
   return re.match('https?://',url)

if __name__=="__main__":
    app = QApplication(sys.argv) 
    if len(sys.argv) == 3:
        if url_check(sys.argv[1]) == None:
            print "网址请输http:// or https://"
        else:
            ps = Pagescreen(sys.argv[1], sys.argv[2], [])
            ps.shot()
            sys.exit(app.exec_())#启动事件循环
    else:
        print "Opps！参数输入错误，要求2个参数，网址 保存名"
