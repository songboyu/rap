# -*- coding: utf-8 -*- 
# RAP: Reply & Post

# Local config
import re

from utils import *
import handlers

import config

# Export functions
def reply(post_url, src):
    """Reply post_url with specific data provided by src.
    Call site-specific functions to reply according to post_url.
    src is a dict, may contain the following keys:
        nickname: optional for those sites accept anonymous comments
        subject: optional
        content: the content of comments
        username: only for those sites require login
        password: only for those sites require login 
        TTL: config.max_try by default if not supplied
        proxies: '' by default if not supplied
    For all the keys in src, `utf8` coding is expected.
    return (True, log)/(False, log) for reply successed/failed.
    Handle exceptions siliently by logging.
    """

    logger = RAPLogger(post_url)

    # Get specific handler
    # For example:
    # 'dwnews\.com/news': ('dwnews_news', 'OUT'),
    for pattern, handler in config.dispatch_rule.items():
        if re.search(pattern, post_url):
            real_reply = getattr(handlers, 'reply_' + handler[0])
            break
    else:
        logger.error('No reply handler')
        return (False, str(logger))

    # Fill the default src
    if 'TTL' not in src:
        src['TTL'] = config.max_try
    if 'proxies' not in src:
        src['proxies'] = ''
    # Log the username and password if necessary
    if 'username' in src and 'password' in src:
        logger.info('Account: ' + src['username'] + '/' + src['password'])
    else:
        logger.info('Account: none/none')

    # Use http instead of https
    post_url = post_url.replace('https', 'http')

    # Real reply
    try:
        r, log = real_reply(post_url, src)
        return (r, str(logger) + log)
    except:
        logger.error(get_traceback())
        return (False, str(logger))


def post(post_url, src):
    """Post on post_url with specific data provided by src.
    post_url is the homepage of specific forum section.
    src is a dict, may contain the following keys:
        subject: the title of post 
        content: the content of post
        username: username
        password: password
        TTL: config.max_try by default if not supplied
        proxies: '' by default if not supplied
    For all the keys in src, `utf8` coding is expected.
    return (url, log)/('', log) for reply successed/failed.
    Handle exceptions siliently by logging.
    """

    logger = RAPLogger(post_url)

    # Get specific handler
    for pattern, handler in config.dispatch_rule.items():
        if re.search(pattern, post_url):
            real_post = getattr(handlers, 'post_' + handler[0])
            break
    else:
        logger.error('No post handler')
        return ('', str(logger))

    # Fill the default src
    if 'TTL' not in src:
        src['TTL'] = config.max_try
    if 'proxies' not in src:
        src['proxies'] = ''
    # Log the username and password if necessary
    if 'username' in src and 'password' in src:
        logger.info('Account: ' + src['username'] + '/' + src['password'])
    else:
        logger.info('Account: none/none')

    # Use http instead of https
    post_url = post_url.replace('https', 'http')

    # Real post
    try:
        url, log = real_post(post_url, src)
        return (url, str(logger) + log)
    except:
        logger.error(get_traceback())
        return ('', str(logger))


def get_account_info(website, src):
    """Get account info on specific website.
    src is a dict, may contain the following keys:
        username: username
        password: password
        TTL: config.max_try by default if not supplied
        proxies: '' by default if not supplied
    For all the keys in src, `utf8` coding is expected.
    return (info, log)/({}, log) for reply successed/failed.
    Handle exceptions siliently by logging.
    """

    logger = RAPLogger(src['username'])

    # Get specific handler
    for pattern, handler in config.dispatch_rule.items():
        if re.search(pattern, website):
            real_get_account_info = getattr(handlers, 'get_account_info_' + handler[0])
            break
    else:
        logger.error('No account handler')
        return ({}, str(logger))

    # Fill the default src
    if 'TTL' not in src:
        src['TTL'] = config.max_try
    if 'proxies' not in src:
        src['proxies'] = ''
    # Log the username and password if necessary
    if 'username' in src and 'password' in src:
        logger.info('Account: ' + src['username'] + '/' + src['password'])
    else:
        logger.info('Account: none/none')

    # Real get account info
    try:
        info, log = real_get_account_info(src)
        return (info, str(logger) + log)
    except:
        logger.error(get_traceback())
        return ({}, str(logger))
