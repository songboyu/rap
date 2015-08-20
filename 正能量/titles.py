import os

a12 = os.listdir('2015-08-12')
a13 = os.listdir('2015-08-13')
a14 = os.listdir('2015-08-14')
a15 = os.listdir('2015-08-15')
a16 = os.listdir('2015-08-16')
a17 = os.listdir('2015-08-17')

titles = a12 + a13 + a14 + a15 + a16 + a17
f = open('titles.txt','w')
for t in titles:
	f.write(t[:-4]+'\n')
f.close()