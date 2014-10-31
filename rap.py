# -*- coding: utf-8 -*- 
# RAP: Reply & Post

# Local config
import re

from utils import *
import handlers

# Export functions
def reply(post_url, src):
    """Reply post_url with specific data provided by src.
    Call site-specific functions to reply according to post_url.
    Src is a dict, may contain the following keys:
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
    for pattern, handler in config.dispatch_rule.items():
        if re.search(pattern, post_url):
            real_reply = getattr(handlers, 'reply_' + handler[0])
            break
    else:
        logger.error('No handler')
        return (False, str(logger))

    # Fill the default src
    if 'TTL' not in src:
        src['TTL'] = config.max_try
    if 'proxies' not in src:
        src['proxies'] = ''
    print src
    # Log the username and password if necessary
    if src['username'] and src['password']:
        logger.debug('Account: ' + src['username'] + '/' + src['password'])
    else:
        logger.debug('Account: none/none')

    # Use http instead of https
    post_url = post_url.replace('https', 'http')

    # Real reply
    try:
        r, log = real_reply(post_url, src)
        return (r, str(logger) + log)
    except Exception as e:
        logger.error(str(type(e)) + ' ' + str(e))
        return (False, str(logger))
