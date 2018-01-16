import os
from time import sleep,time
from subprocess import Popen, PIPE


EXP_TIME = 16*60

IFACE_IN = "eth0"
IFACE_OUT = "eth0"
RX_PCKS = '/sys/class/net/'+IFACE_IN+'/statistics/rx_packets'
RX_BYTES = '/sys/class/net/'+IFACE_IN+'/statistics/rx_bytes'
TX_PCKS = '/sys/class/net/'+IFACE_OUT+'/statistics/tx_packets'
TX_BYTES = '/sys/class/net/'+IFACE_OUT+'/statistics/tx_bytes'

out,err = Popen(["pgrep", "-fn", '(squid)*/etc/squid3/squid.conf'],stdout=PIPE).communicate()
SQUID_PID = out.strip()
#For older version of squid
if not SQUID_PID:
	SQUID_PID =Popen(["pgrep", "-fn", '(squid)*-D -sYC'],stdout=PIPE).communicate()
	SQUID_PID = out.strip()

#OPENVPN_PID = max(check_output(['pgrep','-f','openvpn']).strip().split())

SQUID_CMD = ["top","-b", "-n", "1", "-p", SQUID_PID, "|", "tail", "-1", "|", "head", "-3"] 
#OPENVPN_CMD = ["top","-b", "-n", "1", "-p", OPENVPN_PID, "|", "tail", "-1", "|", "head", "-3"]

HOSTNAME = Popen(['hostname'], stdout=PIPE).communicate()[0].strip()

FILE = "results_proxy_%s" % HOSTNAME

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
	#p2 = Popen(["tail", "-2"], stdin=p1.stdout, stdout=PIPE)
	#p3 = Popen(["head", "-1"], stdin=p2.stdout, stdout=PIPE)
	p1.stdout.close()
	#p2.stdout.close()
	#output, err = p3.communicate()
	output, err = p2.communicate()
	return output.strip().split()[8]

def getTotalCPU():
	squid_cpu = getCPU(SQUID_PID)
	#openvpn_cpu = getCPU(OPENVPN_PID)
	#total = float(openvpn_cpu)+float(squid_cpu)
	total = float(squid_cpu)
	return total

r_p, r_b, t_p,t_b = getNetCounters()
#with open(FILE,"wb") as outfile:
#	outfile.write("time,rx_packets,rx_bytes,tx_packets,tx_bytes,cpu\n")
outfile = open(FILE,"wb")
outfile.write("time,rx_packets,rx_bytes,tx_packets,tx_bytes,cpu\n")
outfile.close()

t = 0
START = time()

rx_p, rx_b, tx_p, tx_b = getNetCounters()
r_p1 = rx_p - r_p
r_b1 = rx_b - r_b
t_p1 = tx_p - t_p
t_b1 = tx_b - t_b
r_p = rx_p
r_b = rx_b
t_p = tx_p
t_b = tx_b
cpu = getTotalCPU()
t = time()-START
#with  open(FILE,"ab") as outfile:
#	outfile.write("{0:.1f},{1},{2},{3},{4},{5:.1f}\n".format(t,r_p1, r_b1, t_p1, t_b1,cpu))
outfile = open(FILE,"ab")
outfile.write("{0:.1f},{1},{2},{3},{4},{5:.1f}\n".format(t,r_p1, r_b1, t_p1, t_b1,cpu))
outfile.close()
if False:
	while t < (EXP_TIME+15):
		sleep(0.6855)
		rx_p, rx_b, tx_p, tx_b = getNetCounters()
		r_p1 = rx_p - r_p
		r_b1 = rx_b - r_b
		t_p1 = tx_p - t_p
		t_b1 = tx_b - t_b
		r_p = rx_p
		r_b = rx_b
		t_p = tx_p
		t_b = tx_b
		cpu = getTotalCPU()
		t = time()-START
		#with open(FILE,"ab") as outfile:
		#	outfile.write("{0:.1f},{1},{2},{3},{4},{5:.1f}\n".format(t,r_p1, r_b1, t_p1, t_b1,cpu))

