# -*- coding: utf-8 -*-
"""RAP Server by tornado

@author: sniper 
@since: 2015-3-7
"""

import re
import json
import logging
import logging.config

import yaml
import concurrent
import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.concurrent

import handlers
import config
import utils

# Load local configurations.
CONFIG = yaml.load(open('config.yaml'))
# Logging config.
logging.config.dictConfig(CONFIG)


class CommentHandler(tornado.web.RequestHandler):
    """CommentHandler"""

    # Thread pool executor.
    executor = concurrent.futures.ThreadPoolExecutor(CONFIG['max_worker'])
    
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        r, log = yield self._comment(json.loads(self.request.body))
        self.write(json.dumps({'result': r, 'log': log}))
        self.finish()

    @tornado.concurrent.run_on_executor
    def _comment(self, params):
        # Convert unicode to utf8.
        for key in params:
            params[key] = params[key].encode('utf8')
        logger = utils.RAPLogger(params['url'])

        # Get specific handler
        # For example:
        # 'dwnews\.com/news': ('dwnews_news', 'OUT'),
        for pattern, handler in config.dispatch_rule.items():
            if re.search(pattern, params['url']):
                real_reply = getattr(handlers, 'reply_' + handler[0])
                break
        else:
            logger.error('No reply handler')
            return (False, str(logger))

        # Prepare arguments.
        src = {
            'subject': params['title'],
            'content': params['content'],
            'username': params['account'],
            'password': params['password'],
            'TTL': config.max_try,
        }

        try:
            src['proxies'] = {params['proxy_type']: params['proxy_type'] + '://' + params['proxy_ip'] + ':' + params['proxy_port']}
        except:
            src['proxies'] = ''

        # Real reply.
        try:
            r, log = real_reply(params['url'], src)
            return (r, str(logger) + log)
        except:
            logger.exception('Reply Error')
            return (False, str(logger))


class PostHandler(tornado.web.RequestHandler):
    """PostHandler"""

    # Thread pool executor.
    executor = concurrent.futures.ThreadPoolExecutor(CONFIG['max_worker'])
    
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        url, log = yield self._post(json.loads(self.request.body))
        self.write(json.dumps({'url': url, 'log': log}))
        self.finish()

    @tornado.concurrent.run_on_executor
    def _post(self, params):
        # Convert unicode to utf8.
        for key in params:
            params[key] = params[key].encode('utf8')
        logger = utils.RAPLogger(params['website'])

        if params['website'] not in config.website_rule:
            logger.error('No post handler')
            return (False, str(logger))
        real_post = getattr(handlers, 'post_' + config.website_rule[params['website']][0])

        # Prepare arguments.
        src = {
            'subject': params['title'],
            'content': params['article'],
            'username': params['account'],
            'password': params['password'],
            'TTL': config.max_try,
        }

        try:
            src['proxies'] = {params['proxy_type']: params['proxy_type'] + '://' + params['proxy_ip'] + ':' + params['proxy_port']}
        except:
            src['proxies'] = ''

        # Real post.
        try:
            url, log = real_post(config.website_rule[params['website']][1], src)
            return (url, str(logger) + log)
        except:
            logger.exception('Post Error')
            return ('', str(logger))


class PraiseHandler(tornado.web.RequestHandler):
    """PraiseHandler"""

    # Thread pool executor.
    executor = concurrent.futures.ThreadPoolExecutor(CONFIG['max_worker'])
    
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        r, log = yield self._praise(json.loads(self.request.body))
        self.write(json.dumps({'result': r, 'log': log}))
        self.finish()

    @tornado.concurrent.run_on_executor
    def _praise(self, params):
        logger = utils.RAPLogger(params['url'])

        for pattern, handler in config.praise_rule.items():
            if re.search(pattern, params['url']):
                real_thumb_up = getattr(handlers, 'thumb_up_' + handler)
                break
        else:
            logger.error('No praise handler')
            return False

        # Prepare arguments.
        src = {'TTL': config.max_try, 'extra': params['extra']}
        if 'account' in params:
            src['username'] = params['account']
        if 'password' in params:
            src['password'] = params['password']

        try:
            src['proxies'] = {params['proxy_type']: params['proxy_type'] + '://' + params['proxy_ip'] + ':' + params['proxy_port']}
        except:
            src['proxies'] = ''

        # Real thumb up.
        try:
            r, log = real_thumb_up(params['url'], src)
            return (r, str(logger) + log)
        except:
            logger.exception('Thumb up error')
            return (False, str(logger))


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Welcome to the cheetah API.')


def main():
    application = tornado.web.Application([
        (r'/', MainHandler),
        (r'/comment', CommentHandler),
        (r'/post', PostHandler),
        (r'/praise', PraiseHandler),
    ])

    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
