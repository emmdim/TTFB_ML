import urllib2
import json
import random
import time

TIMEOUT = 2
TZDB_KEY = '459K79ZDCGC9'
# 10 is chosen semi-arbitrarily, depending on the total number of nodes
RETRIES = 10
URL = 'http://api.timezonedb.com/v2/get-time-zone?format=json&format=json&by=zone&by=zone&zone=America/Chicago&zone=Europe/Madrid&key=%s' % TZDB_KEY

def getEET():
	random.seed()
	for n in range(0,RETRIES):
		req = urllib2.Request(URL)
		opener = urllib2.build_opener()
		try:
			f = opener.open(req, timeout=TIMEOUT)
		except Exception:
			print "Time request failed, attempting new one.."
			# Create randomness for the concurrent requests when bootstrapping
			time.sleep(random.random())
		else:
			result = json.loads(f.read())
			print result['timestamp']
			return result['timestamp']