# -*- coding: utf-8 -*-
"""RAP Server by tornado

@author: sniper 
@since: 2015-3-7
"""
import os
import random
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
import get_ip
import register_handler

# Load local configurations.
CONFIG = yaml.load(open('config.yaml'))
# Logging config.
logging.config.dictConfig(CONFIG)


def build_response_from_log(log):

    errors = {
        '未知错误': 10000,
        '登录失败': 10001,
        '评论失败': 10002,
        '发帖失败': 10003,
        '评论过于频繁': 10004,
        '发帖过于频繁': 10005,
        '验证码错误': 10006,
        '网络异常': 10007,
        '点赞失败': 10008,
        '尚未实现': 10009,
        '用户名已被他人注册': 10010,
        '邮箱已被他人注册' : 10011,
        '上传头像失败': 100012,
    }
    if 'ConnectionError' in log or 'HTTPConnectionPool' in log:
        description = '网络异常'
    elif '验证码' in log:
        description = '验证码错误'
    elif re.search('No \w+ handler', log):
        description = '尚未实现'
    elif 'Login Error' in log:
        description = '登录失败'
    elif 'Reply Error' in log:
        description = '评论失败'
    elif 'Post Error' in log:
        description = '发帖失败'
    elif 'Thumb Up Error' in log:
        description = '点赞失败'
    elif '用户名已被他人注册' in log:
        description = '用户名已被他人注册'
    elif '邮箱已被他人注册' in log:
        description = '邮箱已被他人注册'
    elif 'uploadavatar Error' in log:
        description = '上传头像失败'
    else:
        description = '未知错误'

    return json.dumps({
        'result':'false',
        'httpStatusCode': 500,
        'description': description,
        'errorCode': errors[description],
    })


class CommentHandler(tornado.web.RequestHandler):
    """CommentHandler"""

    # Thread pool executor.
    executor = concurrent.futures.ThreadPoolExecutor(CONFIG['max_worker'])
    
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        r, log = yield self._comment(self.request.arguments)
        if r:
            self.write(json.dumps({'result': 'true'}))
        else:
            self.write(build_response_from_log(log))
        self.finish()

    @tornado.concurrent.run_on_executor
    def _comment(self, params):
        # Convert unicode to utf8.
        for key in params:
            params[key] = params[key][0]
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
            'content': params['content'],
            'TTL': config.max_try,
        }

        if 'account' in params:
            src['username'] = params['account']
        if 'password' in params:
            src['password'] = params['password']
        if 'title' in params:
            src['subject'] = params['title']

        try:
            src['proxies'] = {params['proxy_type']: params['proxy_type'] + '://' + params['proxy_ip'] + ':' + params['proxy_port']}
        except:
            pass

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
        url, log = yield self._post(self.request.arguments)
        if url:
            self.write(json.dumps({'result': 'true', 'url': url}))
        else:
            self.write(build_response_from_log(log))
        self.finish()

    @tornado.concurrent.run_on_executor
    def _post(self, params):
        # Convert unicode to utf8.
        for key in params:
            params[key] = params[key][0]
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
            pass
            
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
        r, log = yield self._praise(self.request.arguments)
        if r:       
            self.write(json.dumps({'result': 'true'}))
        else:
            self.write(build_response_from_log(log))
        self.finish()

    @tornado.concurrent.run_on_executor
    def _praise(self, params):
        for key in params:
            params[key] = params[key][0]
        logger = utils.RAPLogger(params['url'])

        for pattern, handler in config.praise_rule.items():
            if re.search(pattern, params['url']):
                real_thumb_up = getattr(handlers, 'thumb_up_' + handler)
                break
        else:
            logger.error('No praise handler')
            return False

        src = {'TTL': config.max_try, 'extra': eval(params['extra'])}
        if 'account' in params:
            src['username'] = params['account']
        if 'password' in params:
            src['password'] = params['password']

        try:
            src['proxies'] = {params['proxy_type']: params['proxy_type'] + '://' + params['proxy_ip'] + ':' + params['proxy_port']}
        except:
            pass

        # Real thumb up.
        try:
            r, log = real_thumb_up(params['url'], src)
            return (r, str(logger) + log)
        except:
            logger.exception('Thumb Up Error')
            return (False, str(logger))


class IpHandler(tornado.web.RequestHandler):
    """IpHandler"""

    # Thread pool executor.
    executor = concurrent.futures.ThreadPoolExecutor(16)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        ip = yield self._ip()
        self.write(json.dumps(ip))
        self.finish()

    @tornado.concurrent.run_on_executor
    def _ip(self):
        ip = []
        ip = get_ip.getip()
        return ip


class AccoutRegisterHandler(tornado.web.RequestHandler):
    """AccoutRegisterHandler"""

    # Thread pool executor.
    executor = concurrent.futures.ThreadPoolExecutor(16)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        result = yield self._account(self.request.arguments)
        if result == '注册成功':
            self.write(json.dumps({'result': 'true'}))
        else:
            self.write(build_response_from_log(result))
        self.finish()

    @tornado.concurrent.run_on_executor
    def _account(self,params):
        # Convert unicode to utf8.
        for key in params:
            params[key] = params[key][0]
        # Prepare account infomation.
        src = {
            'username': params['account'],
            'password': params['password'],
            'email': params['email'],
        }
        try:
            src['proxies'] = {params['proxy_type']: params['proxy_type'] + '://' + params['proxy_ip'] + ':' + params['proxy_port']}
            print src['proxies']
        except:
            src['proxies'] = ''
        real_submit = getattr(register_handler,'submit_' + config.account_rule[params['website']])
        result = real_submit(src)
        return result

class UploadHeadImage(tornado.web.RequestHandler):
    """UploadHeadImage"""

    # Thread pool executor.
    executor = concurrent.futures.ThreadPoolExecutor(16)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        head_url, log = yield self._upload_head(self.request.arguments)
        if head_url:       
            self.write(json.dumps({'result': 'true','head_url':head_url}))
        else:
            self.write(build_response_from_log(log))
        self.finish()

    @tornado.concurrent.run_on_executor
    def _upload_head(self,params):
        # Convert unicode to utf8.
        for key in params:
            params[key] = params[key][0]
        # Prepare account infomation.
        logger = utils.RAPLogger(params['website'])

        if params['website'] not in config.website_rule:
            logger.error('No upload_head_handler handler')
            return (False, str(logger))
        real_upload_head_handler = getattr(handlers, 'upload_head_' + config.website_rule[params['website']][0])
        heads = os.listdir('head')
        src = {
            'username': params['account'],
            'password': params['password'],
            'TTL': config.max_try,
            'head': 'head/' + random.choice(heads)
        }
        try:
            src['proxies'] = {params['proxy_type']: params['proxy_type'] + '://' + params['proxy_ip'] + ':' + params['proxy_port']}
        except:
            pass
        try:
            head_url, log = real_upload_head_handler(src)
            return (head_url, str(logger) + log)
        except:
            logger.exception('uploadavatar Error')
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
        (r'/ip', IpHandler),
        (r'/account/register', AccoutRegisterHandler),
        (r'/account/upload_head', UploadHeadImage),
    ])

    application.listen(7777)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
