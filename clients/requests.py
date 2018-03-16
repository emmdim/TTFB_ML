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

sys.path.append("../")
from getEET import getEET

USER = 'david.pinilla'
PASS = r'|Jn 5DJ\\7inbNniK|m@^ja&>C'

PROXIES = {
    0 : '10.139.40.85',
    1 : '10.139.40.122',
    2 : '10.138.57.2',
    3 : '10.138.85.130',
    4 : '10.139.17.4',
    5 : '10.139.37.194',
    6 : '10.138.25.67',
    7 : '10.228.192.210', # BCNRossello208 36508
    8 : '10.139.38.2', #13953-knoppix.guifi.net 13953 Olot
    9 : '10.138.71.3',#8258-elpipa Centelles
    10 : '10.34.100.145', #Girona 17732-ProxySGElectronics1
    11 : '10.155.1.101',# 47181-BisbProxy Baix Emporda
    12 : '10.155.7.3', # 	23164-PALF-ProxyTorretes50 Palafrugell
    #15 :

}

URL = "http://ovh.net/files/1Mb.dat"

# Periodicity of requests
INTERVAL = 10 # 10 Minutes

HOSTNAME = Popen(['hostname'], stdout=PIPE).communicate()[0].strip()
RESULT_FILE = "results/results_client_%s" % HOSTNAME
LOG_FILE = "results/log_client_%s" % HOSTNAME

def get_cmd(proxy):
        cmd='curl -x '+proxy+':3128 -U '+USER+':\"'+PASS+'\" -m 180 -w \"%{time_total},%{http_code},%{time_starttransfer}\" -H \"Cache-control: private\" '+URL+' -o /dev/null -s'
        #print cmd
        return cmd

def timestamp2str(timestamp):
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def timestamp2epoch(timestamp):
    return (timestamp - datetime.datetime(1970,1,1)).total_seconds()

def run(real_timestamp, local_timestamp):
    """ Makes every INTERVAL parallel http requests using all the
        available proxies.
        First measurement is in random timestamp. The rest happen
        at every 0,10,20 etc. seconds
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
        processes = {proxy:Popen(shlex.split(get_cmd(proxy)), stdout=PIPE, stderr=PIPE) for i,proxy in PROXIES.iteritems()}
        for proxy,p in processes.iteritems():
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
            print "PID:{}\tTimestamp:{}\tTotalTime:{}\tTTFB:{}\tCode:{}\tProxy:{}".format(p.pid,timestamp2str(real_now),total,ttfb,code,proxy)
            with open(RESULT_FILE,"a") as fil:
                fil.write("{},{},{},{},{}\n".format(timestamp2epoch(real_now), proxy, ttfb, total, code))
        # Find how many seconds are left to sleep, if any, and sleep
        last_local_now = datetime.datetime.now()
        ##Calculate interval without caring if seconds end in 0
        ##interval = (local_now + datetime.timedelta(seconds=10)) - last_local_now
        ##if interval.total_seconds() > 0:
        ##  time.sleep(interval.total_seconds())
        last_real_now = real_now + (last_local_now - local_now)
        #Calculate interval based on that the last digit of seconds has to be zero
        # Mod 7 leads to 60 seconds
        if (real_now.second / 10) == (last_real_now.second / 10):
            remaining_seconds = (((real_now.second / 10 ) + 1) % 7) * 10 - last_real_now.second
        elif (real_now.second / 10) > (last_real_now.second / 10):
            #Change of minute
            remaining_seconds = 0
        else:
            #Change of 10th of second
            remaining_seconds = 0
        interval = remaining_seconds if remaining_seconds > 0 else 0
        #interval = (10 - (last_real_now.second % 10)) if last_real_now.second != 0 else 0
        time.sleep(interval)

def boostrap(real_timestamp, local_timestamp):
    """ Runs when the experiment is started """
    with open(LOG_FILE,"w") as fil:
            fil.write("{} : START Experiment starting\n".format(timestamp2str(real_timestamp)))
    with open(RESULT_FILE,"w") as fil:
        fil.write("timestamp,proxy,ttfb,total_time,code\n")
    run(real_timestamp, local_timestamp)

def restart(real_timestamp, local_timestamp):
    """" Runs when the experiment is detected as stopped"""
    try:
        with open(RESULT_FILE, "rb") as fil:
            last_time = (list(fil)[-1]).split(',')[0]
            last_time = datetime.datetime.fromtimestamp(float(last_time))
            with open(LOG_FILE, "a") as fil1:
                fil1.write("{} : ERROR Experiment stopped at {}\n".format(timestamp2str(real_timestamp), timestamp2str(last_time)))
    except Exception:
        with open(LOG_FILE, "a") as fil:
            fil.write("{} : ERROR Experiment stopped but couldn't find last measurement\n".format(timestamp2str(real_timestamp)))
    run(real_timestamp, local_timestamp)

if __name__ == '__main__':
    real_timestamp = datetime.datetime.utcfromtimestamp(getEET())
    local_timestamp = datetime.datetime.now()
    if len(sys.argv) == 2:
        if sys.argv[1] == "start":
            boostrap(real_timestamp, local_timestamp)
        elif sys.argv[1] == "restart":
            restart(real_timestamp, local_timestamp)
    else:
        with open(LOG_FILE, "a") as fil:
            fil.write("{} : Command run without argument\n".format(timestamp2str(real_timestamp)))
