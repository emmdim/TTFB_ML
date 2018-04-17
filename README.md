# TTFB_ML
TTFB Measurements in guifi.net 

## Installation

### Prepare local environment
```
$pip install virtualenv
$git clone https://github.com/emmdim/TTFB_ML.git && cd TTFB_ML

## Or if you want a local branch like the client_side one
## git clone -b client_side https://github.com/emmdim/TTFB_ML.git && cd TTFB_ML

$virtualenv venv
$source venv/bin/activate
$pip install --upgrade pip
$pip install -r requirements.txt 
```
###  Prepare remote environment

DURING THE FOLLOWING STEP SUDO ACTIONS WILL PROMPT FOR PASSWORDS 

Copy your private key to the TTFB_ML folder name as `key` and your public key in the same place named as key.pub

Configure the clients addresses in the `clients` variable inside the `fabfile.py`. The addresses need to be in the format `user@ip`
The same needs to be done for the `servers`

Add the necessary entries to `ssh-config` for each used client and server.

Install your public key to the clients executing:
```
fab clients_upload_pubkey
```
Since the servers are more to be used with more care you have to install by yourself your public key to them.

The ssh_config file is an ssh configuration file that contains information for that can be leveraged when connecting with ssh key. Please modify  in this step according to your needs.

Then, prepare the environment for the servers and the clients:
```
fab servers_deploy
fab clients_deploy
```
All the functions from this point on can be modified to fill the needs. The existing version creates necessary directories, downloads necessary packages, downloads the project code, and installs a virtualenv where necessary.

## Developing and experimenting
The part of the modules of the code concerning the servers are placed in the servers folder. Similarly for the clients.

The `clients_pull` and the `servers_pull` update the code on the clients and the servers respectively.

The rest of the functions in the fabfile can be customized as needed.

The `getEET.py` module provides the getEET function that returns a UNIX timestamp and can be used to synchronize servers and clients.

### Clients
The `requests.py` module contains the logic for the periodical requests from the clients to the servers.

The `check-running.sh` script can be installed as a cronjob to monitor if the `requests.py` module is alive and take action otherwise.

### Clients
The `monitor.py` module contains the logic for the monitoring of the squid proxy and other metrics, like RX,TX etc.

The `check-running.sh` script can be installed as a cronjob to monitor if the `requests.py` module is alive and take action otherwise.
