import rap
import logging, logging.handlers
import sys

def get_account_info(website, src):
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    handler = logging.handlers.TimedRotatingFileHandler('log/log', 'D', 1, 0)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger('').addHandler(handler)

    # Filter requests log
    requests_log = logging.getLogger('requests')
    requests_log.setLevel(logging.ERROR)

    return rap.get_account_info(website, src)

if __name__ == '__main__':
    #info,log = get_account_info('bbs.163.com/bbs/',
    #                 {'username':'kulala1982',
    #                 'password':'13936755635'})
    info,log = get_account_info('bbs.eulam.com',
                     {'username':'shiduojiuo',
                      'password':'1qazxsw2'})
    print info