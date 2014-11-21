# -*- coding: utf-8 -*-
# Utils.py provides some util functions for Reply & Post

import requests
import logging, unittest
from datetime import datetime

import config

################################################################################
# RAP Exceptions

class RAPException(Exception):
    def __init__(self, value):
        self.value = value

class RAPCaptchaException(RAPException):
    def __str__(self):
        if self.value == 0:
            return '0=> Timeout'
        elif self.value == -1:
            return '-1=> Timeout, params error, recognition error or others'
        elif self.value == -2:
            return '-2=> Insufficient funds'
        elif self.value == -3:
            return '-3=> Unbound'
        elif self.value == -4:
            return '-4=> Time expired'
        elif self.value == -5:
            return '-5=> User authentication failed'
        elif self.value == -6:
            return '-6=> File format error'
        else:
            return 'Undefined exception %d' % self.value

class RAPMaxTryException(RAPException):
    def __str__(self):
        return 'Exceed maximum attempt times for %s' % self.value

################################################################################
# Helper functions

# HTTP interface of chaoren dama
def crack_captcha(raw_captcha):
    import binascii, json
    payload = {
        'softid': config.chaoren_softwareid,
        'username': config.chaoren_username,
        'password': config.chaoren_password,
        'imgdata': binascii.b2a_hex(raw_captcha).upper(),
    }
    try:
        r = requests.post('http://api2.sz789.net:88/RecvByte.ashx', 
            data=payload,
            proxies={'http': ''})
        res = r.json()
        if res['info'] != 1:
            raise RAPCaptchaException(res['info'])
        return res['result']
    except requests.ConnectionError:
        return crack_captcha(raw_captcha)

# Extract hidden value
def hidden_value(form, x):
    return form.find(attrs={'name': x})['value']

# Process CDATA XML
def strip_cdata(xml):
    html = xml.replace('<![CDATA[', '')
    html = html.replace(']]>', '')
    return html

# Fill the form automatically
def get_datadic(form, code='utf8'):
    datadic = {}
    for tag in form.findAll(attrs={'name': True}):
        datadic[tag['name'].encode(code)] = tag['value'].encode(code) if 'value' in tag.attrs else ''
    return datadic

# Get host from url
def get_host(url):
    url = url.replace('https', 'http')
    return '/'.join(url.split('/')[:3]) + '/'

# CLI decorator for RAP handlers.
# Pass parameters of `fn` to OS by command line and collect the results.
# So that we can perform an external call beyond Python such as casperjs..
# Function body of `fn` is ignored, this is just a bridge between Python and OS.
# Both the input and output of this function are expected to be `utf8` format.
def cli(cmd_prefix):
    def real_decorator(fn):
        def wrapper(post_url, src):
            # cmd is a list instead of str in case of parameters with white
            # spaces or quotes.
            cmd = cmd_prefix + [post_url]
            for k, v in src.items():
                cmd += ['--%s=%s' % (k, v)]
                
            # Coding format convert.
            from sys import platform
            if 'win' in platform:
                # Default cmd coding format is `gbk` on Chinese version Windows.
                cmd = [x.decode('utf8').encode('gbk') for x in cmd]
            else:
                # Not implemented
                # TODO: Convert the encoding if necessary on Linux.
                pass

            import subprocess
            try:
                # Also capture standard error in the result.
                r = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False)
                return (True, r)
            except subprocess.CalledProcessError as e:
                return (False, e.output)

        return wrapper
    return real_decorator


################################################################################
# Helper classes

# RAP Session
class RAPSession():
    def __init__(self, src):
        self.s = requests.Session()
        # Fake user agent.
        self.s.headers['User-Agent'] = config.user_agent
        # Use proxies if have one.
        self.s.proxies = src['proxies']
        # Set the max redirect times or it will take too long.
        self.s.max_redirects = config.max_redirects
        # timeout can only be set in http actions instead of session object.

    def get(self, url, **kwargs):
        kwargs['timeout'] = config.http_timeout
        return self.s.get(url, **kwargs)

    def post(self, url, **kwargs):
        kwargs['timeout'] = config.http_timeout
        return self.s.post(url, **kwargs)

# Returnable logger
class RAPLogger():
    def __init__(self, module):
        self.buf = ''
        self.logger = logging.getLogger(module)

    def __str__(self):
        return self.buf

    def info(self, msg):
        if isinstance(msg, unicode):
            msg = msg.encode('utf8')
        self.logger.info(msg)
        self.buf += ' - '.join([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'INFO', msg]) + '\n'

    def error(self, msg):
        if isinstance(msg, unicode):
            msg = msg.encode('utf8')
        self.logger.exception(msg)
        self.buf += ' - '.join([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'ERROR', msg]) + '\n'

################################################################################
# Test

class UtilsTest(unittest.TestCase):

    def test_captcha_ok(self):
        raw_captcha = '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00L\x00\x00\x00\x1c\x08\x06\x00\x00\x00\xcb\x19Y\xdc\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x03#IDAThC\xed\x97\xbfk\x14A\x14\xc7\xcfba\xcd\x91\x1ch#F\xc1"\x86\x80\x85`\xb4\x10\xc5\xabD/\xa2 \x1e"X\xd9\x04Q\xb0\xf0G@\xc1B\xff\x83\xf4\x11+\xb1\xb3L\xe9\xc5\xca\x03K\x854\x16\xfe\x13\xb6\x8e\xf3\x9d}o};\xfbfv\x85\xddM\x02\xf7\x81/\xb7\xfbv\xf6\xe6\xf6\xc3\x9b\xd9\xa4\xd7\x05\xc3\xf7\x93T\x86\xca3\xea\xe2\x0b\xf4C\xc3f\xd4E\x93(C\xc3f\xd4E\x93\xc8\xa1!\xed\xf3\xf5\xcb\xd2\x9d\xba\x99~\xbe\xbcN\xb7\xed+.\xde\xd8\xbd\xa6I\x94\xa1\xa1\xdd\x03i\x9a\xccX\xe8\xd6\xc6\x99\xbc\\]A \x8cJA4\x8924\xac\x1d\xa6\xdb\x1b\'\xe8\xd0\xb1\xf3p4\x8a\x85\x865\x06\x8b\xc2q\x1dYuhM\xe0\xf8\xca\xd3[\x88/-\x86&\xd1\x0f\r\x8d"E1M\tk\x1dH{|\xf7\xd9\x03\x16H\xe5V\xd0D1\x07F\x18\x83NCX\xdc\xff\x084\x1fz\x86\x0eK\xb0\xa4\x90(p\xe0dI\xfc%ZG \x84i\x81$>\xa6\xa1*\x07Z\x18\x88\xedk\xbe@)(\x14\xba5H\x93\xc2\xd2\xef\x1fOr\xa8\xd4\r\xbe\xb4\xb3\xbf\x0f/\xd2a\x01\x96\xf2z|\xff\x11B\xe5\xbcN\xa7\x1a\xe6\x97\x8d\x1d\x10\x0c\x8d\x8b"\x05u.\x89\xc0\x0f-E\x13\xa6-9\xd9y\xf8\xa4r\x89\xeb\xf6;\xedM\xc1Llhh\x01\x16s\xe8\xd8\xc0\x8d\x91\xf7<\x0f\xdc\xd3\x16\x98,\x1a\x96\xc6\x9bx\xa8\x8bd\x9d\x05r\xdc\x00;D>,:\x8d\xea%d\xf7 \xa8\xc5d\xbb\x9b:\x02\x93q\x18:O\xdc\xe7\x9bO\xa7\x86\xb1\xb7\x1d\x08Id \xed\xf8` \x1e\xf2\x88\xd9rsdh\x82<\xf2{!\xce\xafu\xd5e\x98\x84#\xc9jIb\xce,\x1du\xd7B{\x19\xa8\x92\xc5\xe0\xa1\xec\xa0,\xe9\xbc\xd9\xea\x8bs\x9b\xc8C\xe7\x9d)d\x81P\xbd50\tGR\xa8\xe3EP\xb5\xf9\xd3i\x10m\xef\xf1\x83\xeb4\xbc\x00\x8b\x96\x1dI\xec\xa90-9!i!Y\xca\x12\xd3\xe4h5\x9f\\\n\x9dK\xdc>\x18\xdb\x0b\xdb\x00\x93i)\xf1jwx\x9e\x0e\x1dZw\tA\x05\xb8\x03\xe4\xdf^\x85%j\xa3tP\xbe\xd1k2c\xd7\xda\xc2$\xd9d"}\x93^X6\xa7\xbf\xbd]\x93\xc1`\x00i\xe8\xb6\xbaKQ\xb2\xb9\xfdg\xe1\xea\xbd\x9f\xb7\xf1\x99\xce\xf5\xcd\x8e\x9d\xcf~A\x96$5\xa3\xb9\x05\x83k\x1c\x8cy\x97\xe0zb^\xd4\xbcFS\xb5\x02\t\xca\xe2~D\x9a\xbd\x15\xf1vL\xbc\x1f\xb8:\xdd\x1c#\xe7~<Y\xc7\'\x0b\xe3z,7W\xe6\xff\x89\xb1\xd1\x96c`Y\xed\x9b\xe5\x88I8>\xb1k\x0e\x96\x15\xfbWJ\xe0\x96\x9a\xfd\xb2<k\x97\x96\xcd\xc6\xa2\xac\xd9n\xd1\xbb\xda]\xd7\xa4\xf0r\x8e\xbcY\x1b\x03\x13\xc8Hb\xd7rX\x18\x8ekHs\x0fl\x07\xe7A\x8d;G\xd4JD\xf6(W\xdf\x8b\xee\x92\x13\x86\xea*\xf2\x8dY!\xad L[\x8e\xdaf\x0fX\x18\xc2/\r\x8bVk\x15LR\x95J\xfc?1"\xd2J\x1d&S\xd1%\xc1{\xbbX\x8a\x12L\x16J\x1b\xa8\x0f^\xe7\xa1e\x97!\x15\x82g4C\xaf\xf7\x17n+\xe3b\n\x17]\x9c\x00\x00\x00\x00IEND\xaeB`\x82'
        self.assertEqual(crack_captcha(raw_captcha), '8750')

    def test_captcha_error(self):
        raw_captcha = 'Not a valid image!'
        try:
            crack_captcha(raw_captcha)
        except Exception as e:
            self.assertEqual(str(e), '-6=> File format error')

if __name__ == '__main__':
    unittest.main()

