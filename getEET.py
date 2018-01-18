import urllib2
import json

TIMEOUT = 2
TZDB_KEY = '459K79ZDCGC9'
URL = 'http://api.timezonedb.com/v2/get-time-zone?format=json&format=json&by=zone&by=zone&zone=America/Chicago&zone=Europe/Madrid&key=%s' % TZDB_KEY

def getEET():
	req = urllib2.Request(URL)
	opener = urllib2.build_opener()
	f = opener.open(req, timeout=TIMEOUT)
	result = json.loads(f.read())
	return result['timestamp']