#!/bin/sh
sudo killall nginx
sudo /usr/local/nginx/sbin/nginx 
echo 'nginx restart is success'
killall python
python ./manage.py runfcgi method=threaded host=127.0.0.1 port=3033
echo 'python ./manage.py runfcgi restart is success' 
