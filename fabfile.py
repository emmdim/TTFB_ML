#
#fabfile.py
#
from __future__ import with_statement
from fabric.api import env, task, run, local, cd, prefix, show, roles, parallel
from fabric.contrib import files
from contextlib import contextmanager as _contextmanager


clients = {'SEG_1':'pirate@10.228.205.132',
#'SEG_2':'10.1.9.132',
#'SEG_3':'10.1.10.25',
'SEG_6':'pirate@10.1.15.70',
#'SEG_7':'10.139.40.142', #Not connecting
#'SEG_10':'10.228.206.40' #Not connecting
}

servers = {
	'SERV1' : 'root@10.138.85.130',
	'SERV2' : 'root@10.138.120.66',
	'SERV3' : 'root@10.138.77.2'
 
}

import os

env.shell = "/bin/bash"
env.virtualenv = os.path.join(os.getcwd(),'venv')
env.activate = '. %(virtualenv)s/bin/activate' % env
env.code_dir = os.getcwd()
env.roledefs = {
	'clients' : [ip for name,ip in clients.iteritems()],
	'servers' : [ip for name,ip in servers.iteritems()]
}

PUB_KEY = "~/.ssh/manosupc.pub"

@_contextmanager
def virtualenv():
	with cd(env.virtualenv), prefix(env.activate), cd(env.code_dir):
		yield



@task
def deploy_local():
	#local('virtualenv venv')
	with show('debug'):
		with cd(env.code_dir):
			if not os.path.exists('venv'):
				local('virtualenv venv')
			else:
				print 'exists'
		with virtualenv():
			local('pip install --upgrade pip')
			local('pip install -r requirements.txt')

@task
@parallel
@roles('clients','servers')
def test_clients():
	run('date', shell=False)


@task
@parallel
def check_keys():
	run('cat ~/.ssh/authorized_keys',shell=False)

@task
#@parallel
#@roles('clients')
def upload_pubkey_clients(pubkey_file=PUB_KEY):
	with show('debug'):
		with open(os.path.expanduser(pubkey_file)) as fd:
			ssh_key = fd.readline().strip()
			files.append('/home/pirate/.ssh/authorized_keys', ssh_key, shell=False)

@task
@parallel
@roles('servers')
def test_servers():
	run('date', shell=False)

@task
@parallel
@roles('clients','servers')
def start_experiment():
	run('date', shell=False)

@task
@parallel
@roles('clients','servers')
def stop_experiment():
	pass


@task
@parallel
@roles('clients','servers')
def check_experiment():
	pass

@task
@parallel
@roles('clients','servers')
def get_results():
	pass


