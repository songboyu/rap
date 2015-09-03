#!/bin/bash
logdir="log/"`date +%Y%m%d`
echo $logdir
if [ ! -d  $logdir ]; then
  mkdir $logdir
fi
(nohup python batch_post.py 45  > $logdir"/45.log"  2>&1 &)
(nohup python batch_post.py 62  > $logdir"/62.log"  2>&1 &)
(nohup python batch_post.py 44  > $logdir"/44.log"  2>&1 &)
(nohup python batch_post.py 33  > $logdir"/33.log"  2>&1 &)
(nohup python batch_post.py 8  > $logdir"/8.log"  2>&1 &)
(nohup python batch_post.py 13  > $logdir"/13.log"  2>&1 &)
(nohup python batch_post.py 2  > $logdir"/2.log"  2>&1 &)
(nohup python batch_post.py 17  > $logdir"/17.log"  2>&1 &)
(nohup python batch_post.py 37  > $logdir"/37.log"  2>&1 &)
(nohup python batch_post.py 15 > $logdir"/15.log" 2>&1 &)
(nohup python batch_post.py 3 > $logdir"/3.log" 2>&1 &)
(nohup python batch_post.py 12 > $logdir"/12.log" 2>&1 &)
(nohup python batch_post.py 34 > $logdir"/34.log" 2>&1 &)
(nohup python batch_post.py 60 > $logdir"/60.log" 2>&1 &)
(nohup python batch_post.py 39 > $logdir"/39.log" 2>&1 &)
(nohup python batch_post.py 10 > $logdir"/10.log" 2>&1 &)
(nohup python batch_post.py 5 > $logdir"/5.log" 2>&1 &)
