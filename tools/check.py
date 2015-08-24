# -*- coding: utf-8 -*-

import os
import sys
import requests
from multiprocessing.pool import ThreadPool

import socks
import socket
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 1080)
socket.socket = socks.socksocket

def check(code, bbs, title, url):
    try:
        resp = requests.get(url)
    except:
        print 'error'
        return;

    try:
        content = resp.content.decode('utf8').encode('utf8')
    except:
        content = resp.content.decode('gbk').encode('utf8')

    global ok_list    
    if title in content:
        print url
        ok_list.append((code, bbs, title, url))
    else:
        print 'error'


def get(dirname):
    for filename in os.listdir(dirname):
        with open(dirname + '/' + filename) as f:
            for line in f.readlines():
                code, bbs, title, url = line.strip('\n').split('\t')
                if not url: continue
                yield (code, bbs, title, url)


def check_all(dirname, workers=20):
    global ok_list
    ok_list = []

    pool = ThreadPool(workers)
    for code, bbs, title, url in get(dirname):
        pool.apply_async(check, (code, bbs, title, url))
    pool.close()
    pool.join()

    with open('check.txt', 'w') as f:
        for one in ok_list:
            f.write('\t'.join(one) + '\n')


def main():
    dirname = sys.argv[1]
    try:
        workers = int(sys.argv[2])
        check_all(dirname, workers)
    except:
        check_all(dirname)

if __name__ == '__main__':
    main()

