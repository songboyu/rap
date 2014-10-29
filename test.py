# -*- coding: utf-8 -*-
"""beanstalkc测试

@author: HSS
@since: 2014-10-229
@summary: beanstalkc测试

"""
import json
import logging, logging.config

import beanstalkc
import yaml

if __name__ == '__main__':
    CONFIG = yaml.load(open('config.yaml'))
    logging.config.dictConfig(CONFIG)
    bean = beanstalkc.Connection(CONFIG['beanstalk']['ip'],
                                 CONFIG['beanstalk']['port'])
    bean.watch('rap_server')
    data = {
        'post_url':'http://bbs.news.163.com/bbs/society/465546412.html?param=conc4',
        'src':
            {
                'username':'kulala1982',
                'password':'13936755635',
                'content':'好久不见大家了',
                'nickname':'',
                'subject':'',
                'proxies':''
            }
    }
    job_body = json.dumps(data)
    bean.put(job_body)