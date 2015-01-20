# -*- coding: utf-8 -*- 
# RAP: Reply & Post

import re

from utils import *
import handlers

# Export functions
def get_account_info(website, src):
    logger = RAPLogger(src['username'])

    # Get specific handler
    for pattern, handler in config.dispatch_rule.items():
        if re.search(pattern, website):
            real_get_account_info = getattr(handlers, 'get_account_info_' + handler[0])
            break
    else:
        logger.error('No handler')
        return (False, str(logger))

    # Fill the default src
    if 'TTL' not in src:
        src['TTL'] = config.max_try
    if 'proxies' not in src:
        src['proxies'] = {}

    # Log the username and password if necessary
    if src['username'] and src['password']:
        logger.info('Account: ' + src['username'] + '/' + src['password'])
    else:
        logger.info('Account: none/none')
    # Real get account info
    faild_info = {'Error':'Failed to get account info'}
    try:
        info, log = real_get_account_info(src)
        return (info, str(logger) + log)
    except Exception as e:
        logger.error(str(type(e)) + ' ' + str(e))
        return (faild_info, str(logger))
