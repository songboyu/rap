# -*- coding: utf-8 -*-
import requests
import json

if __name__ == '__main__':
    payload = {
    'website': '无忧',
    'account': 'dwwuu12ud51',
    'password': 'heihdei0',
    'email': 'he314s1939239@gmail.com',
    }
    r = requests.post('http://127.0.0.1:7777/account/register', data=payload)
    print r.content
