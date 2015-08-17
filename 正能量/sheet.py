# -*- coding: utf-8 -*-
import os

def main(date):
	dir = 'article_url/'+date + '/'
	ts = os.listdir(dir)
	f = open(u'报表/'+date+'.txt','w')
	for t in ts:
		f.write(open(dir+t).read())
	f.close()

if __name__ == '__main__':
	date = '2015-08-16'
	main(date)