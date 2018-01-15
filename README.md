# TTFB_ML
TTFB Measurements in guifi.net 

## Installation
Prepare Environment
```
$pip install virtualenv
$git clone https://github.com/emmdim/TTFB_ML.git && cd TTFB_ML
$virtualenv venv
$source venv/bin/activate
$pip install --upgrade pip
$pip install -r requirements.txt 
$fab deploy_local
```
Copy your private key to the TTFB_ML folder name as `key`

Install your public key to the servers and clients.
In fabfile.py change:
```
PUB_KEY = "~/.ssh/mykey.pub"
```
Then execute:
```
fab -R
```

## Usage
