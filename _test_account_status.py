# -*- coding: utf-8 -*-
import requests

if __name__ == '__main__':
    payload = {
	    'website': '凯迪',
	    'account': 'kulala1982',
	    'password': '13936755635',
	    # 'proxy_ip': '192.168.60.15',
	    # 'proxy_port': '808',
	    # 'proxy_type': 'http'
    }
    r = requests.post('http://127.0.0.1:7777/account/training/status', data=payload)
    print r.content
