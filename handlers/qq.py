
import requests 

import utils

def thumb_up_qq(post_url, src):
    logger = utils.RAPLogger(post_url)
    sess = utils.RAPSession(src)

    resp = sess.get(src['extra']['target_url'],
        headers={'Referer': post_url},
        params={
        'targetid': post_url.split('/')[-1],
        'callback': 'ding',
        })
    logger.info(resp.content)
    if 'Operation too frequent' in resp.content:
        logger.info('Operation too frequent')
        return(False, str(logger))
    return (True, str(logger))
