# -*- coding: utf-8 -*-
import requests
import json

if __name__ == '__main__':
    payload = {
	    'url': 'http://china.dwnews.com/news/2015-03-11/59640427.html',
	    'proxy_ip': '172.19.103.64',
	    'proxy_port': 8118
    }
    r = requests.post('http://127.0.0.1:7788/get_content_by_url', data=payload)
    print r.content
