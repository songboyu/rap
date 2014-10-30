# -*- coding: utf-8 -*-
"""A general router for beanstalk.

@author: sniper
@since: 2014-10-30
"""

import logging

import beanstalkc

def route(src_queues, dispatcher, beanstalk_ip, beanstalk_port):
    """The message dispatching loop. It watches the queues in `src_queues` and
    then transmit messages to specific queues according to the function 
    `dispatcher`. A message may be transmitted to one or more queues, or it may
    be discarded. All the behaviors are implemented in the function 
    `dispatcher`. `dispatcher` receives the message body as parameter, then it
    return a list of destination queues indicating where this message should be
    transmitted to. The returned list can be empty, which means discard.

    @param src_queues: source beanstalk queues
    @type src_queues: list

    @param dispatcher: a judge function
    @type dispatcher: function

    @param beanstalk_ip: beanstalk server ip
    @type beanstalk_ip: str

    @param beanstalk_port: beanstalk server port
    @type beanstalk_port: int
    """

    logger = logging.getLogger(__name__)
    try:
        bean = beanstalkc.Connection(beanstalk_ip, beanstalk_port)
        for queue in src_queues:
            bean.watch(queue)
        bean.ignore('default')
    except:
        logger.critical('Beanstalk server exception', exc_info=True)
        return

    while True:
        job = bean.reserve()
        # dispatch
        for queue in dispatcher(job.body):
            bean.use(queue)
            bean.put(job.body)
        job.delete()
