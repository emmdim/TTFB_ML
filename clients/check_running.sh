#!/bin/bash
# check_running.sh
# make sure experiment is running.  
pgrep -l -f 'requests.py' > /dev/null
REQUESTS=$?

screen -ls | grep TTFB > /dev/null
SCREEN=$?

if [[ $REQUESTS -eq 0 && $SCREEN -eq 0 ]]; then
	echo "Running"
elif [[ $SCREEN -ne 0 ]]; then
	echo "Screen is not running"
	screen -dmS TTFB python requests.py restart && sleep 1
else
	echo "Requests are not running"
	screen -S TTFB -X stuff "python requests.py restart"$(echo -ne '\015')
fi