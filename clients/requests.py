#requests.py
#For threading solution check:
#Source: http://stackoverflow.com/questions/2632520/what-is-the-fastest-way-to-send-100-000-http-requests-in-python
#
#SERVERS AND CLIENTS TIME SYNCHRONIZATION
#Two timestamps are used. The real timestamp is for reporting.
#In order to make only 1 http request to get the real timestamp the 
#timedelta from the beggining of the experiment to now is measured 
#using the local_timestamp
#NODES AGREEMENT (for example PROXY SELECTION)
#In case of the neceissty of for the agreement on any issue 
#between the nodes the time can be used. Commented inside the run 
#function are parts of the code that would make the clients to agree
#on a common proxy every 10 minutes.

import time
from subprocess import PIPE, Popen
import shlex
import sys
import datetime
from ..getEET import getEET

USER = 'david.pinilla'
PASS = r'|Jn 5DJ\\7inbNniK|m@^ja&>C'

PROXIES = {
    0 : '10.138.85.130',
    1 : '10.138.120.66',
    2 : '10.138.77.2',
}

URL = "http://ovh.net/files/1Mb.dat"

# Periodicity of requests
INTERVAL = 10 # 10 Minutes

HOSTNAME = Popen(['hostname'], stdout=PIPE).communicate()[0].strip()
RESULT_FILE = "results_client_%s" % HOSTNAME
LOG_FILE = "errors_client_%s" % HOSTNAME

def get_cmd(proxy):
        cmd='curl -x '+proxy+':3128 -U '+USER+':\"'+PASS+'\" -m 180 -w \"%{time_total},%{http_code},%{time_starttransfer}\" -H \"Cache-control: private\" '+URL+' -o /dev/null -s'
        print cmd
        return cmd

def timestamp2str(timestamp):
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def timestamp2epoch(timestamp):
    return (timestamp - datetime.datetime(1970,1,1)).total_seconds()

def run(real_timestamp, local_timestamp):
    """ Makes every INTERVAL parallel http requests using all the 
        available proxies.
    """
    ## In case we want the proxy is selected depending on the 
    ##10ths of minutes of the time
    ##now = datetime.datetime.now()
    ##proxy_id  = (real_timestamp.minute/10)  % 3
    ##proxy = PROXIES[proxy_id]
    ##while now < local_timestamp + datetime.timedelta(minutes = 10):
    while True:
        local_now = datetime.datetime.now()
        real_now = real_timestamp + (local_now - local_timestamp)
        processes = {(i,Popen(shlex.split(get_cmd(proxy)), stdout=PIPE, stderr=PIPE)) for i,proxy in PROXIES.iteritems()}
        for i,p in processes.iteritems(): 
            #p.wait()
            #out1, err = p.stdout.read(),p.stderr.read()
            out1, err = p.communicate()
            out1 = out1.split(',')
            # Different implmentations of curl
            if len(out1) == 4:
                total = out1[1]
                code = out1[2]
                ttfb = out1[3]
            else:
                total = out1[0]
                code = out1[1]
                ttfb = out1[2]
            print "PID:{}\t\tTimestamp:{}\tTotalTime:{}\tTTFB:{}\tCode:{}\tProxy:{}".format(p.pid,timestamp2str(real_now),ttfb,code,PROXIES[i])
            with open(RESULT_FILE,"a") as fil:
                fil.write("{},{},{},{},{}\n".format(real_now, PROXIES[i], ttfb, total, code))
            # Find how many seconds are left to sleep, if any, and sleep
            last_local_now = datetime.datetime.now()
            interval = (local_now + datetime.timedelta(seconds=10)) - last_local_now
            if interval.total_seconds() > 0:
                time.sleep(interval.total_seconds())

def boostrap(real_timestamp, local_timestamp):
    """ Runs when the experiment is started """
    with open(LOG_FILE,"w") as fil:
            fil.write("{} : START Experiment starting\n".format(timestamp2str(real_timestamp)))
    with open(RESULT_FILE,"w") as fil:
        fil.write("timestamp,proxy,ttfb,total_time,code\n")
    run(real_timestamp, local_timestamp)

def restart(real_timestamp, local_timestamp):
    """" Runs when the experiment is detected as stopped"""
    with open(RESULT_FILE, "rb") as fil:
        last_time = (list(fil)[-1]).split(',')[0]
        last_time = datetime.datetime.fromtimestamp(last_time)
        with open(LOG_FILE, "a") as fil1:
            fil1.write("{} : ERROR Experiment stopped at {}\n".format(timestamp2str(real_timestamp), timestamp2str(last_time)))
    run(real_timestamp, local_timestamp)

if __name__ == '__main__':
    real_timestamp = datetime.datetime.fromtimestamp(getEET())
    local_timestamp = datetime.datetime.now()
    if sys.argv[1] == "start":
        boostrap(real_timestamp, local_timestamp)
    elif sys.argv[1] == "restart":
        restart(real_timestamp, local_timestamp)
    else:
        with open(LOG_FILE, "a") as fil:
            fil.write("{} : Command run without argument\n".format(timestamp2str(real_timestamp)))

