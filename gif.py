import Image

def processImage(path):
    DURATION = 1000

    im = Image.open(path)
    frames = []
    key = 0
    for i in range(10):
        im.seek(i)
        frames.append(im.load())
        if im.info['duration']>DURATION:
            key = i
    frame = frames[key]

    WIDTH = 100
    HEIGHT = 50

    d = {}
    for i in xrange(WIDTH):
        for j in xrange(HEIGHT):
            k = frames[key][i,j]
            if d.has_key(k):
                d[k][0] += 1
                d[k].append((i,j))
            else:
                d[k] = [1,(i,j)]
    topd = sorted(d.items(),cmp=lambda x,y:cmp(y[1][0],x[1][0]))

    for i in xrange(WIDTH):
        for j in xrange(HEIGHT):
            frame[i,j]=0

    found = 0
    for (k,v) in topd:
        if not isnoise(v[1:]):
            for point in v[1:]:
                frame[point[0],point[1]]=k
            found += 1
        else:
#           print k,'is noise'
            pass
        if found == 4:
            break
    return frame

def printframe(frame,code=-1):
    for i in xrange(WIDTH):
        for j in xrange(HEIGHT):
            if (code == -1 and frame[i,j] !=0) or (code != -1 and frame[i,j]==code) :
                print '*',
            else:
                print '-',
        print

if __name__ == '__main__':
    processImage('1.gif')