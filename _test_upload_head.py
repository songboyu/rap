# -*- coding: utf-8 -*-
import requests
import json

if __name__ == '__main__':
    payload = {
	    'website': '加国无忧论坛',
	    'account': 'baiduqqsougou',
	    'password': 'blueshit',
	    'proxy_ip': '217.15.183.26',
	    'proxy_port': '8080',
	    'proxy_type': 'http'
    }
    r = requests.post('http://127.0.0.1:7777/account/upload_head', data=payload)
    print r.content
