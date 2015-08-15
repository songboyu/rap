# -*- coding: utf-8 -*-

import re
import sys
import time
import random
import threading
import requests
from multiprocessing.pool import ThreadPool


def weighted_choice(weights):
    totals = []
    running_total = 0

    for k, w in weights:
        running_total += w
        totals.append(running_total)

    rnd = random.random() * running_total
    for i, total in enumerate(totals):
        if rnd < total:
            return weights[i][0]


def get_session():
    sess = requests.Session()
    sess.headers['User-Agent'] = 'Mozilla/5\.0 (Windows NT 6\.3; WOW64) AppleWebKit/537\.36 (KHTML, like Gecko) Chrome/37\.0\.2062\.124 Safari/537\.36'
    return sess

def f5_normal(url):
    sess = requests.Session()
    sess.get(url)


def f5_wenxuecity(url):
    sess = get_session()
    resp = sess.get(url)
    f5_url = re.findall(r'(http://count\.wenxuecity\.com.*?)"', resp.content)[0]
    sess.get(f5_url)


def f5_dwnews(url):
    sess = get_session()
    sess.get('http://blog.dwnews.com/index.php',
        params={
            'r': 'club/clubzan',
            'id': re.findall('(\d+)', url)[0],
            'type': 'likes',
            'callback': '?',
        })


def f5(url):
    try:
        if 'wenxuecity' in url:
            f5_wenxuecity(url)
        elif 'dwnews' in url:
            f5_dwnews(url)
        else:
            f5_normal(url)
        print url
    except Exception as e:
        print type(e), str(e)


def go(count, workers=10):
    urls = []
    with open('f5_list.txt') as f:
        for line in f.readlines():
            if line == '\n': continue
            # Default priority is 10.
            try:
                url, str_priority = line.strip().split()
                urls.append((url, int(str_priority)))
            except:
                urls.append((line.strip(), 10))

    pool = ThreadPool(workers)
    for i in range(count):
        url = weighted_choice(urls)
        pool.apply_async(f5, (url,))
    pool.close()
    pool.join()


def main():
    count = int(sys.argv[1])
    try:
        workers = int(sys.argv[2])
        go(count, workers)
    except:
        go(count)

if __name__ == '__main__':
    main()
