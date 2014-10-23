# -*- coding: utf-8 -*- 

# RAP Server: Multi-thread version.
# 2014-7-18
# Start a thread polling database at a specific interval. If there are any reply
# jobs in `reply_job` table satisfy certain criteria, namely `status` equals zero
# and scheduled `reply_time` before current time, polling thread enqueue the jobs
# immediately. Simultaneously, A bunch of reply worker threads get feed from the
# shared queue and perform the reply jobs as soon as possible. Both the polling
# thread and worker threads will run permanently until the main process is killed.

import sys, time
import threading, Queue, MySQLdb
import logging, logging.handlers

import requests
from bs4 import BeautifulSoup

import rap
import server_config as config

# Get url title with utf8 encoding format.
# Put this function here instead of in `rap.py` because this is temporary and
# should not be one part of reply module.
def get_url_title(post_url):
    try:
        r = requests.get(post_url)
        soup = BeautifulSoup(r.content)
        return soup.find('title').text.encode('utf8')
    except:
        return ''

def db_connect():
    return MySQLdb.connect(config.db_ip, config.db_username, config.db_password, config.db_dbname)

def get_site_sign(post_url):
    domain = post_url.split('/')[2]
    return domain.split('.')[-2]

# Polling database every `polling_interval` seconds.
class Poller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global jobs_queue
        jobs_queue = Queue.Queue(config.queue_size)
        while True:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute('set character set "utf8"')
            cursor.execute('select * from reply_job where status = 0 and reply_time < now()')
            rows = cursor.fetchall()
            for row in rows:
                src = {'content': row[2]}
                if row[3]:
                    src['username'] = row[3]
                    src['password'] = row[4]
                if row[5]: src['nickname'] = row[5]
                if row[6]: src['subject'] = row[6]
                if row[7]: src['proxies'] = row[7]
                # Reply job enqueue.
                # Blocking until there is a free slot in the queue.
                jobs_queue.put((row[1], src, row[0]))
                # Set the tag in case of re-enqueueing.
                cursor.execute('update reply_job set status = 1 where job_id = %s', (row[0],))

            conn.commit()       
            conn.close()
            time.sleep(config.polling_interval)

class ReplyWorker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global jobs_queue
        while True:
            # Reply job dequeue.
            # Blocking until there is a new job in the queue.
            post_url, src, job_id = jobs_queue.get()

            url_title = get_url_title(post_url)
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute('set character set "utf8"')
            cursor.execute('update reply_job set status = 1, update_time = now(), url_title = %s where job_id = %s', (url_title, job_id))
            conn.commit()

            r, log = rap.reply(post_url, src)
            # 2 stands for OK and 3 stands for Error.
            status = 2 if r else 3
            cursor.execute('update reply_job set status = %s, error = %s, update_time = now() where job_id = %s', (status, log, job_id))
            if 'Login Error' in log:
                # Set the is_invalid tag of this account.
                r = cursor.execute('update account set is_invalid = 1 where username = %s and site_sign in (select site_sign from site where site_url like %s)', (src['username'], '%' + get_site_sign(post_url) + '%'))
            conn.commit()
            conn.close()

if __name__ == '__main__':
    # Logging system.
    handler = logging.handlers.TimedRotatingFileHandler('log/log', 'D', 1, 0)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logging.getLogger('').addHandler(handler)

    # Filter requests log
    requests_log = logging.getLogger('requests')
    requests_log.setLevel(logging.ERROR)

    Poller().start()
    workers = []
    for i in range(config.workers):
        workers.append(ReplyWorker())
    for worker in workers:
        worker.start()
