# -*- coding: utf-8 -*-
"""Router for rap system.

@author: sniper
@since: 2014-10-30
"""

import re
import json
import logging, logging.config

import yaml
import beanstalkc

import config
import router

def rap_dispatcher(msg):
    """Dispatcher for rap. Transmit in-wall reply job to `rap_in` queue and
    out-wall reply job to `rap_out` queue.

    @param msg: message body of reply job in json format
    @type msg: str

    @return: a list consists of `rap_in` or `rap_out`
    @rtype: list
    """

    src = json.loads(msg)
    for pattern, handler in config.dispatch_rule.items():
        if re.search(pattern, src['post_url']):
            if handler[1] == 'IN':
                return ['rap_in']
            elif handler[1] == 'OUT':
                return ['rap_out']
    # Although no such handler, discarding it will cause some db problems. So
    # pass it to a queue.
    return ['rap_in']


if __name__ == '__main__':
    # Load local configurations.
    CONFIG = yaml.load(open('config.yaml'))
    # Logging config.
    logging.config.dictConfig(CONFIG)

    router.route(['rap_server'], rap_dispatcher, 
                 CONFIG['beanstalk']['ip'], CONFIG['beanstalk']['port'])
    