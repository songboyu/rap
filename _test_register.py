# -*- coding: utf-8 -*-
import requests
import json

if __name__ == '__main__':
    payload = {
    'website': '加国无忧论坛',
    'account': 'dwwuuud5',
    'password': 'heihdei0',
    'email': 'he34s1999@gmail.com',
    }
    r = requests.post('http://127.0.0.1:8888/account/add', data=json.dumps(payload))
    print r.content
