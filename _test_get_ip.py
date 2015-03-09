# -*- coding: utf-8 -*-
import requests
import json

if __name__ == '__main__':
    payload = {
    }
    r = requests.post('http://127.0.0.1:8888/ip', data=json.dumps(payload))
    print r.content
