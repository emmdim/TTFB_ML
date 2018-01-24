#
#fabfile.py
#
from __future__ import with_statement
from fabric.api import env, task, run, local, cd, prefix, show, roles, parallel, settings, sudo, get, execute
from contextlib import contextmanager as _contextmanager


clients = {
'SEG_1':'khulan@10.228.207.65',
'SEG_2':'khulan@10.228.207.66',
'SEG_3':'khulan@10.139.40.87',
'SEG_4':'khulan@10.139.94.108',
}
client_hosts = [v.split('@')[1] for v in clients.values()]

servers = {
	'SERV1' : 'root@10.138.85.130',
	'SERV2' : 'root@10.138.120.66',
	'SERV3' : 'root@10.138.77.2'
 
}
server_hosts = [v.split('@')[1] for v in servers.values()]

servers_ifaces = {
	'10.138.85.130' : 'eth0',
	'10.138.120.66' : 'eth0',
	'10.138.77.2' : 'eth3'

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

env.code_dir_clients = '/home/khulan/ttfb/TTFB_ML/clients/'
env.virtualenv_clients = 'venv'
env.activate_clients  ='. %(virtualenv_clients)s/bin/activate' % env

env.code_dir_servers = '/root/ttfb/TTFB_ML/servers/'
env.virtualenv_servers = 'venv'
env.activate_servers  ='. %(virtualenv_servers)s/bin/activate' % env

PUB_KEY = "key.pub"

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
		sudo('apt-get update', shell=False)
		# Because of error that curl was not installed when cloning
		sudo('apt-get install -y curl python-pip git screen', shell=False)
		# Create experiment directory if not exists
		with settings(warn_only=True):
			if (run("test -d %s" % '/home/khulan/ttfb', shell=False).return_code) == 1:
				print 'Creating working directory'
				run("mkdir %s" % '/home/khulan/ttfb', shell=False)
		with cd('/home/khulan/ttfb'):
			run("sudo pip install virtualenv", shell=False)
			with settings(warn_only=True):
				if (run("test -d %s" % 'TTFB_ML', shell=False).return_code) == 1:
					print 'Cloning repository'
					run("git clone https://github.com/emmdim/TTFB_ML.git", shell=False)
		with cd(env.code_dir_clients):
			run("git pull", shell=False)
			with settings(warn_only=True):
				if (run("test -d %s" % 'venv', shell=False).return_code) == 1:
					print 'Creating Virtual Environment'
					run("virtualenv venv", shell=False)
		with virtualenv_clients():
			run("pip install --upgrade pip", shell=False)
			run("which python", shell=False)


@task
@roles('servers')
def servers_deploy():
	#Skipping virtualenv because of complication from different server OS versios etc.
	with show('debug'):
		# Create experiment directory if not exists
		run('apt-get update', shell=False)
		# Because of error that curl was not installed when cloning
		run('apt-get install -y curl', shell=False)
		# Because of confusion between git and git-fm for olde debian versions
		run('apt-get install -y git-core screen', shell=False)
		with settings(warn_only=True):
			if (run("test -d %s" % '/root/ttfb', shell=False).return_code) == 1:
				print 'Creating working directory'
				run("mkdir %s" % '/root/ttfb', shell=False)
		with cd('/root/ttfb'):
			with settings(warn_only=True):
				if (run("test -d %s" % 'TTFB_ML', shell=False).return_code) == 1:
					print 'Cloning repository'
					#Using git in the url since HTTP does not work for older versions of git
					run("git clone git://github.com/emmdim/TTFB_ML.git", shell=False)
		#Not using env.code_dir_clients cause olde git versions do not pull when in subfolder
		with cd('/root/ttfb/TTFB_ML'):
			run("git pull", shell=False)
			run("ls", shell=False)

@task
@parallel
@roles('clients')
def clients_pull():
	with show('debug'):
		with cd(env.code_dir_clients):
			run("git pull", shell=False)

@task
@parallel
@roles('servers')
def servers_pull():
	with show('debug'):
		with cd('/root/ttfb/TTFB_ML'):
			run("git pull", shell=False)

@task
@parallel
@roles('clients')
def clients_test():
	with virtualenv_clients():
		run("python requests.py start", shell=False)


@task
@parallel
@roles('servers')
def servers_test():
	print env.host
	with cd(env.code_dir_servers):
		run("python monitor.py {} start".format(servers_ifaces[env.host]), shell=False)


@task
@roles('clients')
def check_keys():
	run('cat ~/.ssh/authorized_keys',shell=False)

@task
@roles('clients')
def clients_upload_pubkey(pubkey_file=PUB_KEY):
	with show('debug'):
		with settings(use_ssh_config=False,user='khulan'):
			with settings(warn_only=True):
				if (run("test -d %s" % '/home/khulan/.ssh', shell=False).return_code) == 1:
					print 'Creating .ssh directory'
					run("mkdir %s" % '/home/khulan/.ssh', shell=False)
				run("chmod 700 /home/khulan/.ssh", shell=False)
				if (run("test -d %s" % '/home/khulan/.ssh/authorized_keys', shell=False).return_code) == 1:
					print 'Creating authorized_keys'
					run("touch %s" % '/home/khulan/.ssh/authorized_keys', shell=False)	
				run("chmod 600 /home/khulan/.ssh/authorized_keys", shell=False)
			with open(os.path.expanduser(pubkey_file)) as fd:
				ssh_key = fd.readline().strip()
				run("echo '%s' >> %s" % (ssh_key,'/home/khulan/.ssh/authorized_keys'), shell=False)
				#files.append('/home/khulan/.ssh/authorized_keys', ssh_key, shell=False)

def runbg(cmd):
    return run("screen -dmS TTFB %s && sleep 1" % cmd, shell=False)

@task
@roles('clients','servers')
def start_experiment():
	if env.host in server_hosts:
		with cd(env.code_dir_servers):
			command = "python monitor.py {} start".format(servers_ifaces[env.host])
			execute(runbg,command)
	elif env.host in client_hosts:
		with virtualenv_clients():
			command = "python requests.py start"
			execute(runbg,command)

@task
#@parallel
@roles('clients','servers')
def stop_experiment():
	with settings(warn_only=True):
		run('screen -S TTFB -X quit', shell=False)

@task
@roles('clients','servers')
def check_experiment():
	with settings(warn_only=True):
		run('screen -ls', shell=False)

@task
@roles('clients','servers')
def get_results():
	if env.host in client_hosts:
		with cd(env.code_dir_clients):
			with settings(warn_only=True):
				get('results/results*','clients/results/')
	elif env.host in server_hosts:
		with cd(env.code_dir_servers):
			with settings(warn_only=True):
				get('results/results*','servers/results/')
	else:
		print 'Nothing'

@task
@roles('clients','servers')
def get_logs():
	if env.host in client_hosts:
		with cd(env.code_dir_clients):
			with settings(warn_only=True):
				get('results/log*','clients/results/')
	elif env.host in server_hosts:
		with cd(env.code_dir_servers):
			with settings(warn_only=True):
				get('results/log*','servers/results/')
	else:
		print 'Nothing'