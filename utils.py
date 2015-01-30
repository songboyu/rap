# -*- coding: utf-8 -*-
# Utils.py provides some util functions for Reply & Post

import binascii
import datetime
import logging
import StringIO
import traceback

import requests

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

def print_to_file(content):
    f = open('debug.html','w')
    f.write(content)
    f.close()

# HTTP interface of chaoren dama
def crack_captcha(raw_captcha):
    payload = {
        'softid': config.chaoren_softwareid,
        'username': config.chaoren_username,
        'password': config.chaoren_password,
        'imgdata': binascii.b2a_hex(raw_captcha).upper(),
    }
    try:
        resp = requests.post('http://api2.sz789.net:88/RecvByte.ashx', data=payload)
        json_body = resp.json()
        if json_body['info'] != 1:
            raise RAPCaptchaException(json_body['info'])
        return json_body['result']
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
        try:
            datadic[tag['name'].encode(code)] = tag['value'].encode(code) if 'value' in tag.attrs else ''
        except:
            # Encode error is fairly rare.
            # But when it happens, use the origin value without encoding.
            datadic[tag['name']] = tag['value'] if 'value' in tag.attrs else ''
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


def get_traceback():
    """Return the traceback information."""

    buf = StringIO.StringIO()
    traceback.print_exc(file=buf)
    return buf.getvalue()


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

    def __getattr__(self, method):
        """Forward RAPSession's get, post, etc. to the requests.Session."""

        if method not in ['get', 'options', 'head', 'post', 'put', 'patch', 'delete']:
            # Only forward the methods in the list.
            raise AttributeError('RAPLogger object has no attribute ' + method)          

        def real_method(url, **kwargs):
            kwargs['timeout'] = config.http_timeout
            return getattr(self.s, method)(url, **kwargs)

        return real_method


# Returnable logger
class RAPLogger():
    def __init__(self, module):
        self.buf = ''
        self.logger = logging.getLogger(module)

    def __str__(self):
        return self.buf

    def __getattr__(self, method):
        """Forward RAPLogger's info, error, etc. to the standard logger."""

        if method not in ['debug', 'info', 'warning', 'warn', 'error', 'critical', 'exception']:
            # Only forward the methods in the list.
            raise AttributeError('RAPLogger object has no attribute ' + method)

        def real_method(msg, *args, **kwargs):
            # Convert unicode to utf8 if necessary.
            if isinstance(msg, unicode):
                msg = msg.encode('utf8')
            # Call the real_method
            getattr(self.logger, method)(msg, *args, **kwargs)
             
            # Append traceback to msg.
            if method == 'exception':
                msg += '\n' + get_traceback()
            self.buf += ' - '.join([datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), method.upper(), msg]) + '\n'

        # Just like a decorator.
        return real_method 
