#!/bin/bash
# check_running.sh
# make sure experiment is running.  

if  ! pgrep -l -f 'requests.py' > /dev/null
then
	echo "Stopped"
fi