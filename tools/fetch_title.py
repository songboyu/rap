# -*- coding: utf-8 -*-
import MySQLdb
import requests
from bs4 import BeautifulSoup

def db_connect():
    """数据库连接

    @return:            connection
    @rtype:             MySQLdb.connections.Connection
    """
    return MySQLdb.connect('192.168.8.55', 'root', '123456', 'comment',
                           charset='utf8')
def fetch_title():
        conn = db_connect()
        cursor = conn.cursor()

        cursor.execute('select id, url from reply_url where ISNULL(title) order by insert_time desc')

        for row in cursor.fetchall():
            id, url = row
            print url,

            try: 
                r = requests.get(url)
                soup = BeautifulSoup(r.content)
                # print soup
                h1 = soup.select('h1')
                if len(h1)>0:
                    title = h1[0].text.strip()
                else:
                    title = soup.select('title')[0].text.strip()
                
                print title
                cursor.execute('update reply_url set title = %s where id = %s', (title, str(id)))
                conn.commit()

            except Exception as e:
                print e

        cursor.close()
        conn.close()

if __name__ == '__main__':
    fetch_title()