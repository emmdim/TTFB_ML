#!/bin/bash
# check_running.sh
# make sure experiment is running.  

if  pgrep -l -f 'monitor.py' > /dev/null
then
	echo "Running"
else
	echo "Stopped"
