#For threading solution check:
#Source: http://stackoverflow.com/questions/2632520/what-is-the-fastest-way-to-send-100-000-http-requests-in-python
from time import time,sleep
from subprocess import check_output, PIPE, Popen
import csv
import shlex
import os
import string
import random

USER = 'david.pinilla'
PASS = r'|Jn 5DJ\\7inbNniK|m@^ja&>C'

PROXY = "10.138.120.66"

URL = "http://ovh.net/files/1Mb.dat"

def get_cmd(proxy=PROXY):
        cmd='curl -x '+proxy+':3128 -U '+USER+':\"'+PASS+'\" -m 180 -w \"%{time_total},%{http_code}\" -H \"Cache-control: private\" '+URL+' -o /dev/null -s'
        print cmd
        return cmd


processes = [Popen(shlex.split(get_cmd(PROXY)),stdout=PIPE, stderr=PIPE) for i in range(3)]
#out = 0

#results = [p.stdout.read() for p in processes]
#print results

#if False:
for p in processes: 
    #p.wait()
    #out1, err = p.stdout.read(),p.stderr.read()
    out1, err = p.communicate()
    out = out1.split(',')[1]
    code = out1.split(',')[2]
    print "PID:{}\tTime:{}\tCode:{}\tProxy:{}".format(p.pid,out,code,PROXY)


