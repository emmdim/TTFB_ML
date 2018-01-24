#!/bin/bash
# check_running.sh
# make sure experiment is running.  
IFACE=$1

pgrep -l -f 'monitor.py' > /dev/null
MONITOR=$?

screen -ls | grep TTFB > /dev/null
SCREEN=$?

if [[ $MONITOR -eq 0 && $SCREEN -eq 0 ]]; then
	echo "Running"
elif [[ $SCREEN -ne 0 ]]; then
	echo "Screen is not running"
	screen -dmS TTFB python monitor.py $IFACE restart && sleep 1
else
	echo "Monitor is not running"
	screen -S TTFB -X stuff "python monitor.py $IFACE restart"$(echo -ne '\015')
fi