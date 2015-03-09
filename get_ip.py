#coding:utf-8
import re,time
import urllib2 ,requests
import sys, os

def getip():
    post_url = 'http://www.xici.net.co/nn/'
    s=requests.session()
    r=s.get(post_url)
    page=r.content
    match=re.findall(r'<td>(.*?)</td>',page)
    store = []
    for x in xrange(2,693,7):
        ip = {}
        ip['ip']=match[x].strip('\n')
        ip['port']=match[x+1].strip('\n')
        ip['type']=match[x+3].strip('\n')
        ip['location']=match[x+2].strip('\n')
        store.append(ip)
    return store


if __name__ == "__main__":
    ip = []
    ip = getip()
    print ip
