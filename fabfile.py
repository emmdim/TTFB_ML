#
#fabfile.py
#
from __future__ import with_statement
from fabric.api import env, task, run, local, cd, prefix, show, roles, parallel, sudo, settings
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
env.use_ssh_config = True
env.ssh_config_path = "ssh_config"
env.sudo_prefix = "sudo "

env.code_dir_clients = '/home/pirate/ttfb/TTFB_ML/clients/'
env.virtualenv_clients = 'venv'
env.activate_clients  ='. %(virtualenv_clients)s/bin/activate' % env

env.code_dir_servers = '/root/ttfb/TTFB_ML/servers/'
env.virtualenv_servers = 'venv'
env.activate_servers  ='. %(virtualenv_servers)s/bin/activate' % env

PUB_KEY = "~/.ssh/manosupc.pub"

@_contextmanager
def virtualenv():
	with cd(env.virtualenv), prefix(env.activate), cd(env.code_dir):
		yield

@_contextmanager
def virtualenv_clients():
	with cd(env.virtualenv_clients), prefix(env.activate_clients), cd(env.code_dir_clients):
		yield

@_contextmanager
def virtualenv_servers():
	with cd(env.virtualenv_servers), prefix(env.activate_servers), cd(env.code_dir_servers):
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
@roles('clients')
def clients_deploy():
	#local('virtualenv venv')
	with show('debug'):
		# Create experiment directory if not exists
		if (run("test -d %s" % '/home/pirate/ttfb', shell=False).return_code) == 1:
			print 'Creating working directory'
			run("mkdir %s" % '/home/pirate/ttfb', shell=False)
		with cd('/home/pirate/ttfb'):
			run("sudo pip install virtualenv", shell=False, )
			if (run("test -d %s" % 'TTFB_ML', shell=False).return_code) == 1:
				print 'Cloning repository'
				run("git clone https://github.com/emmdim/TTFB_ML.git", shell=False)
		with cd(env.code_dir_clients):
			run("git pull", shell=False)
			with settings(warn_only=True):
				#run("test -d %s" % env.code_dir_clients+"venv1", shell=False)
				print run("test -d %s" % 'venv', shell=False).return_code
				if (run("test -d %s" % 'venv', shell=False).return_code) == 1:
					print 'Creating Virtual Environment'
					run("virtualenv venv", shell=False)
		with virtualenv_clients():
			run("pip install --upgrade pip", shell=False)
			run("which python", shell=False)


@task
@roles('servers')
def servers_deploy():
	#local('virtualenv venv')
	with show('debug'):
		# Create experiment directory if not exists
		if (run("test -d %s" % '/root/ttfb', shell=False).return_code) == 1:
			print 'Creating working directory'
			run("mkdir %s" % '/root/ttfb', shell=False)
		with cd('/root/ttfb'):
			run("sudo pip install virtualenv", shell=False, )
			if (run("test -d %s" % 'TTFB_ML', shell=False).return_code) == 1:
				print 'Cloning repository'
				run("git clone https://github.com/emmdim/TTFB_ML.git", shell=False)
		with cd(env.code_dir_servers):
			run("git pull", shell=False)
			with settings(warn_only=True):
				#run("test -d %s" % env.code_dir_clients+"venv1", shell=False)
				print run("test -d %s" % 'venv', shell=False).return_code
				if (run("test -d %s" % 'venv', shell=False).return_code) == 1:
					print 'Creating Virtual Environment'
					run("virtualenv venv", shell=False)
		with virtualenv_servers():
			run("pip install --upgrade pip", shell=False)
			run("which python", shell=False)



@task
@parallel
@roles('clients')
def clients_pull():
	with show('debug'):
		with cd(env.code_dir_clients):
			run("git pull", shell=False)

@task
@roles('clients')
def clients_test():
	with virtualenv_clients():
		run("python requests.py", shell=False)


@task
@parallel
@roles('servers')
def servers_test():
	with virtualenv_servers():
		run("python monitor.py", shell=False)


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


