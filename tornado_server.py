# -*- coding: utf-8 -*-
"""RAP Server by tornado

@author: sniper 
@since: 2015-3-7
"""

import re
import json
import thread
import logging
import logging.config

import yaml
import tornado.ioloop
import tornado.web

import handlers
import config
import utils


class CommentHandler(tornado.web.RequestHandler):
    """CommentHandler"""

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
            src['proxies'] = {params['proxy_type']: params['proxy_type'] + '://' + params['proxy_ip'] + ':' + params['proxy_type']}
        except:
            src['proxies'] = ''

        # Real reply.
        try:
            r, log = real_reply(params['url'], src)
            return (r, str(logger) + log)
        except:
            logger.exception('Reply Error')
            return (False, str(logger))

    def post(self):
        # Start comment thread.
        thread.start_new_thread(self._comment, (json.loads(self.request.body),))
        self.write(json.dumps({'result': 'true'}))


class PostHandler(tornado.web.RequestHandler):
    """PostHandler"""

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
            src['proxies'] = {params['proxy_type']: params['proxy_type'] + '://' + params['proxy_ip'] + ':' + params['proxy_type']}
        except:
            src['proxies'] = ''

        # Real post.
        try:
            url, log = real_post(config.website_rule[params['website']][1], src)
            return (url, str(logger) + log)
        except:
            logger.exception('Post Error')
            return ('', str(logger))

    def post(self):
        # Start post thread.
        thread.start_new_thread(self._post, (json.loads(self.request.body),))
        self.write(json.dumps({'result': 'true'}))


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello world!')


application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/comment', CommentHandler),
    (r'/post', PostHandler),
])


if __name__ == "__main__":
    # Load local configurations.
    CONFIG = yaml.load(open('config.yaml'))
    # Logging config.
    logging.config.dictConfig(CONFIG)

    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
    