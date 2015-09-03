# -*- coding: utf-8 -*-

import sys

import MySQLdb
# from PyQt4.QtGui import *
# from PyQt4.QtCore import *
# from PyQt4.QtWebKit import *

# from screen_print_pyqt import Pagescreen
from screen_print_selenium import Pagescreen

def db_connect():
    """数据库连接

    @return:            connection
    @rtype:             MySQLdb.connections.Connection
    """
    return MySQLdb.connect('192.168.8.55', 'root', '123456', 'comment',
                           charset='utf8')
def auto_screen_print():
    try: 
        ps = Pagescreen()
        conn = db_connect()
        cursor = conn.cursor()

        cursor.execute('select urlmd5, url, title, post_time from posts where screen_print = 0 order by tid desc')

        for row in cursor.fetchall():
            urlmd5, url, title, post_time = row
            print url

            # ps = Pagescreen(url, urlmd5+'.png', [])
            # ps.shot()
            # app.exec_()
            if ps.capture(url, 'capture/'+urlmd5+'.png'):
                cursor.execute('update posts set screen_print = 1 where urlmd5="'+urlmd5+'"')
                conn.commit()

        cursor.close()
        conn.close()
        ps.quit()
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

if __name__ == '__main__':
    # app = QApplication(sys.argv)
    auto_screen_print()

