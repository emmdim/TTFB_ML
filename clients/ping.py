from subprocess import PIPE, Popen
import shlex

PROXIES = {
    0 : '10.228.12.2', # 	31050-SLLProxy sallent
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
    12 : '10.91.122.66',# 67873-CRD10FN01-Proxy Cardedeu
}


HOSTNAME = Popen(['hostname'], stdout=PIPE).communicate()[0].strip()
RESULT_FILE = "results/results_ping_client_%s" % HOSTNAME

CMD =  'ping -c 30'

#print("Proxy,Hops,Min,Avg,Max,Mdev")
with open(RESULT_FILE, "w") as fil:
    fil.write("Proxy,Hops,Min,Avg,Max,Mdev\n")


def getCmd(proxy):
    return CMD + ' ' + proxy


for i,proxy in PROXIES.iteritems():
    p = Popen(shlex.split(getCmd(proxy)), stdout=PIPE, stderr=PIPE)
    out1, err = p.communicate()
    out1 = out1.strip().split('\n')
    hops = 64 - int(out1[1].split(':')[1].split(' ')[2].split('=')[1])
    stats = out1[-1].split('=')[1].split('/')
    stats = map(lambda x: x.strip(), stats)
    stats[-1] = stats[-1].split(' ')[0]
    min1, avg, max1, mdev = stats
    #print("{},{},{},{},{},{}".format(proxy,hops,min1,avg,max1,mdev))
    with open(RESULT_FILE, "a") as fil:
        fil.write("{},{},{},{},{},{}\n".format(proxy,hops,min1,avg,max1,mdev))
