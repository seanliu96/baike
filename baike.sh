#!/bin/bash
pidof python # 检测程序是否运行
while [ 1 ]    # 判断程序上次运行是否正常结束
do
    echo "Process exits with errors! Restarting!"
    scrapy crawl baike > /dev/null 2>&1   #重启程序
done
echo "Process ends!"
