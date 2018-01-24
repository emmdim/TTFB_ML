import os
from time import sleep,time
from subprocess import Popen, PIPE
import sys
import datetime

sys.path.append("../")
from getEET import getEET

IFACE_IN = sys.argv[1]
#Assuming both Ifaces are the same
IFACE_OUT = IFACE_IN
RX_PCKS = '/sys/class/net/'+IFACE_IN+'/statistics/rx_packets'
RX_BYTES = '/sys/class/net/'+IFACE_IN+'/statistics/rx_bytes'
TX_PCKS = '/sys/class/net/'+IFACE_OUT+'/statistics/tx_packets'
TX_BYTES = '/sys/class/net/'+IFACE_OUT+'/statistics/tx_bytes'

out,err = Popen(["pgrep", "-fn", '(squid)*/etc/squid3/squid.conf'],stdout=PIPE).communicate()
SQUID_PID = out.strip()
#For older version of squid
if not SQUID_PID:
	out, err =Popen(["pgrep", "-fn", '(squid)*-D -sYC'],stdout=PIPE).communicate()
	SQUID_PID = out.strip()

#OPENVPN_PID = max(check_output(['pgrep','-f','openvpn']).strip().split())

SQUID_CMD = ["top","-b", "-n", "1", "-p", SQUID_PID, "|", "tail", "-1", "|", "head", "-3"] 
#OPENVPN_CMD = ["top","-b", "-n", "1", "-p", OPENVPN_PID, "|", "tail", "-1", "|", "head", "-3"]



HOSTNAME = Popen(['hostname'], stdout=PIPE).communicate()[0].strip()

RESULT_FILE = "results/results_proxy_%s" % HOSTNAME
LOG_FILE = "results/log_proxy_%s" % HOSTNAME


def timestamp2str(timestamp):
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def timedelta_total_seconds(timedelta):
    return (
        timedelta.microseconds + 0.0 +
        (timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6

def timestamp2epoch(timestamp):
    return timedelta_total_seconds(timestamp - datetime.datetime(1970,1,1))

def getCounter(counter):
	out, err = Popen(['cat',counter],stdout=PIPE).communicate()
	return out.strip()

def getNetCounters():
	rx_p = int(getCounter(RX_PCKS))
	rx_b = int(getCounter(RX_BYTES))
	tx_p = int(getCounter(TX_PCKS))
	tx_b = int(getCounter(TX_BYTES))
	return rx_p, rx_b, tx_p, tx_b

def getCPU(pid):
	p1 = Popen(["top","-b", "-n", "1", "-p", SQUID_PID], stdout=PIPE)
	p2 = Popen(["grep", SQUID_PID], stdin=p1.stdout, stdout=PIPE)
	p3 = Popen(["top", "-bn1"], stdout=PIPE)
	p4 = Popen(["awk",'NR>7{s+=$9} END {print s/4}'], stdin=p3.stdout, stdout=PIPE)
	#p2 = Popen(["tail", "-2"], stdin=p1.stdout, stdout=PIPE)
	#p3 = Popen(["head", "-1"], stdin=p2.stdout, stdout=PIPE)
	p1.stdout.close()
	#p2.stdout.close()
	#output, err = p3.communicate()
	output, err = p2.communicate()
	squidCPU = output.strip().split()[8]
	output, err = p4.communicate()
	totalCPU = output.strip()
	return squidCPU, totalCPU

def getTotalCPU():
	squidCPU,total = getCPU(SQUID_PID)
	#openvpn_cpu = getCPU(OPENVPN_PID)
	#total = float(openvpn_cpu)+float(squid_cpu)
	try :
		squidTotal = float(squidCPU)
	except ValueError:
		# For some reason (probably locale) fabric shell uses top that produces
		# floats with commas instead of periods in one of the servers
		squidTotal = float('.'.join(squidCPU.split(',')))
	try :
		totalCPU = float(total)
	except ValueError:
		# For some reason (probably locale) fabric shell uses top that produces
		# floats with commas instead of periods in one of the servers
		totalCPU = float('.'.join(total.split(',')))
	return squidTotal, totalCPU

def run(real_timestamp, local_timestamp, counters):
	r_p, r_b, t_p,t_b = counters
	while True:
		local_now = datetime.datetime.now()
		real_now = real_timestamp + (local_now - local_timestamp)
		rx_p, rx_b, tx_p, tx_b = getNetCounters()
		r_p1 = rx_p - r_p
		r_b1 = rx_b - r_b
		t_p1 = tx_p - t_p
		t_b1 = tx_b - t_b
		r_p = rx_p
		r_b = rx_b
		t_p = tx_p
		t_b = tx_b
		squidCPU,totalCPU = getTotalCPU()
		outfile = open(RESULT_FILE,"ab")
		#Changed to support Python 2.4
		print("%s,%s,%s,%s,%s,%.2f,%.2f\n" % (timestamp2str(real_now),r_p1, r_b1, t_p1, t_b1,squidCPU,totalCPU))
		outfile.write("%s,%s,%s,%s,%s,%.2f,%.2f\n" % (timestamp2epoch(real_now),r_p1, r_b1, t_p1, t_b1,squidCPU,totalCPU))
		outfile.close()
		# Update packet and byte counters
		r_p, r_b, t_p,t_b = rx_p, rx_b, tx_p, tx_b
		# Find how many seconds are left to sleep, if any, and sleep
		last_local_now = datetime.datetime.now()
		last_real_now = real_now + (last_local_now - local_now)
		if (last_real_now.second % 2) == 1:
			sleep(1)
		else:
			sleep(2)


def boostrap(real_timestamp, local_timestamp):
    """ Runs when the experiment is started """
    outfile = open(LOG_FILE,"w")
    outfile.write("%s : START Experiment starting\n" % timestamp2str(real_timestamp))
    outfile.close()
    outfile = open(RESULT_FILE,"w")
    outfile.write("timestamp,rx_packets,rx_bytes,tx_packets,tx_bytes,SquidCPU,TotalCPU\n")
    outfile.close()
    #r_p, r_b, t_p,t_b = getNetCounters()
    counters = getNetCounters()
    run(real_timestamp, local_timestamp, counters)

def restart(real_timestamp, local_timestamp):
    """" Runs when the experiment is detected as stopped"""
    try:
	    infile = open(RESULT_FILE, "rb")
	    last_time = (list(infile)[-1]).split(',')[0]
	    infile.close()
	    last_time = datetime.datetime.fromtimestamp(last_time)
	    outfile = open(LOG_FILE, "a")
	    outfile.write("{} : ERROR Experiment stopped at {}\n" % (timestamp2str(real_timestamp), timestamp2str(last_time)))
	    outfile.close()
	except Exception:
		outfile = open(LOG_FILE, "a")
		outfile.write("{} : ERROR Experiment stopped but couldn't find last measurement\n" % timestamp2str(real_timestamp))
		outfile.close()
	run(real_timestamp, local_timestamp)

if __name__ == '__main__':
    real_timestamp = datetime.datetime.utcfromtimestamp(getEET())
    local_timestamp = datetime.datetime.now()
    if len(sys.argv) == 3:
        if sys.argv[2] == "start":
            boostrap(real_timestamp, local_timestamp)
        elif sys.argv[2] == "restart":
            #restart(real_timestamp, local_timestamp)
            pass
    else:
        outfile = open(LOG_FILE, "a")
        outfile.write("%s : Command run without argument\n" % timestamp2str(real_timestamp))
        outfile.close()

