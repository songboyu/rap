#!/bin/bash
logdir="log/"`date +%Y%m%d`
echo $logdir
if [ ! -d  $logdir ]; then
  mkdir $logdir
fi
(nohup python batch_post.py 2 > $logdir"/2.log" 2>&1 &)
(nohup python batch_post.py 3 > $logdir"/3.log" 2>&1 &)
(nohup python batch_post.py 5 > $logdir"/5.log" 2>&1 &)
(nohup python batch_post.py 7 > $logdir"/7.log" 2>&1 &)
(nohup python batch_post.py 9 > $logdir"/9.log" 2>&1 &)
(nohup python batch_post.py 10 > $logdir"/10.log" 2>&1 &)
(nohup python batch_post.py 13 > $logdir"/13.log" 2>&1 &)
(nohup python batch_post.py 15 > $logdir"/15.log" 2>&1 &)
(nohup python batch_post.py 16 > $logdir"/16.log" 2>&1 &)
(nohup python batch_post.py 19 > $logdir"/19.log" 2>&1 &)
(nohup python batch_post.py 21 > $logdir"/21.log" 2>&1 &)
(nohup python batch_post.py 22 > $logdir"/22.log" 2>&1 &)
(nohup python batch_post.py 6 > $logdir"/6.log" 2>&1 &)
(nohup python batch_post.py 12 > $logdir"/12.log" 2>&1 &)
(nohup python batch_post.py 18 > $logdir"/18.log" 2>&1 &)
(nohup python batch_post.py 4 > $logdir"/4.log" 2>&1 &)
