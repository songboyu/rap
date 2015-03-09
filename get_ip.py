#coding:utf-8
import re,time
import urllib2 ,requests
import sys, os

def real_time(params):
    if '分钟' in params:
        params = params.strip('分钟前')
        return time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time() - int(params)*60))
    else:
        params = params.strip('小时前')
        return time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time() - int(params)*3600))
def getip():
    post_url = 'http://www.xici.net.co/'
    s=requests.session()
    r=s.get(post_url)
    page=r.content
    match=re.findall(r'<td>(.*?)</td>',page)
    country = re.findall(r'<img alt="(.*?)"',page)
    name = ['nn','nt','wn','wt','']
    store = []
    temp = {}
    tem = 0
    for x in xrange(1,560,7):
        ip = {}
        ip['country'] = country[x/7].strip('\n')
        ip['ip'] = match[x+0].strip('\n')
        ip['port'] = match[x+1].strip('\n')
        ip['location'] = match[x+2].strip('\n')
        ip['anonymous'] = match[x+3].strip('\n')
        ip['type'] = match[x+4].strip('\n')
        ip['time'] = real_time(match[x+5].strip('\n'))
        store.append(ip)
        if len(store) == 20:
            temp[name[tem]] = store
            store = []
            tem = tem + 1
    return temp


if __name__ == "__main__":
    ip = {}
    ip = getip()
    print ip
