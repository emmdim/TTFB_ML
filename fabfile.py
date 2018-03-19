#
# fabfile.py
#
from __future__ import with_statement
from fabric.api import env, task, run, local, cd, prefix, show, roles, parallel, settings, sudo, get, execute
from contextlib import contextmanager as _contextmanager
from fabric.contrib.project import rsync_project
from time import sleep
import os
import glob
import datetime as dt


clients = {
    'SEG_1': 'khulan@10.228.207.65',
    'SEG_2': 'khulan@10.228.207.66',
    'SEG_3': 'khulan@10.139.40.87',
    'SEG_4': 'khulan@10.139.94.108',
}
client_hosts = [v.split('@')[1] for v in clients.values()]

servers = {
    #	'SERV1' : 'root@10.138.85.130', #AjntSrv
    #	'SERV2' : 'root@10.138.120.66', #proxy
    #	'SERV3' : 'root@10.138.77.2' #PratsAjntSrv1
}

server_hosts = [v.split('@')[1] for v in servers.values()]

servers_ifaces = {
    '10.138.85.130': 'eth0',
    '10.138.120.66': 'eth0',
    '10.138.77.2': 'eth3'

}

env.shell = "/bin/bash"
env.virtualenv = os.path.join(os.getcwd(), 'venv')
env.activate = '. %(virtualenv)s/bin/activate' % env
env.code_dir = os.getcwd()
env.roledefs = {
    'clients': [ip for name, ip in clients.iteritems()],
}
env.use_ssh_config = True
env.ssh_config_path = "ssh_config"
env.sudo_prefix = "sudo "

env.code_dir_clients = '/home/khulan/ttfb-client/TTFB_ML/clients/'
env.virtualenv_clients = 'venv'
env.activate_clients = '. %(virtualenv_clients)s/bin/activate' % env


PUB_KEY = "key.pub"


@_contextmanager
def virtualenv():
    with cd(env.virtualenv), prefix(env.activate), cd(env.code_dir):
        yield


@_contextmanager
def virtualenv_clients():
    with cd(env.virtualenv_clients), prefix(env.activate_clients), cd(env.code_dir_clients):
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
        # Install necessary packages,
        sudo('apt-get install -y curl python-pip git screen rsync', shell=False)
        # Create experiment directory if not exists
        with settings(warn_only=True):
            if (run("test -d %s" % '/home/khulan/ttfb-client', shell=False).return_code) == 1:
                print 'Creating working directory'
                run("mkdir %s" % '/home/khulan/ttfb-client', shell=False)
        with cd('/home/khulan/ttfb-client'):
            run("sudo pip install virtualenv", shell=False)
            with settings(warn_only=True):
                if (run("test -d %s" % 'TTFB_ML', shell=False).return_code) == 1:
                    print 'Cloning repository'
                    run("git clone -b client_side https://github.com/emmdim/TTFB_ML.git", shell=False)
        with cd(env.code_dir_clients):
            run("git pull", shell=False)
            with settings(warn_only=True):
                if (run("test -d %s" % 'venv', shell=False).return_code) == 1:
                    print 'Creating Virtual Environment'
                    run("virtualenv venv", shell=False)
        with virtualenv_clients():
            run("pip install --upgrade pip", shell=False)
            run("which python", shell=False)
            # Ceate crontab file if it does not exist and assign it local user permissions
            sudo(
                'crontab -l -u `logname` &> /dev/null; if [ $? -gt 0 ]; then sudo touch /var/spool/cron/crontabs/`logname` ; fi', shell=False)
            sudo(
                'chown `logname`:`logname` /var/spool/cron/crontabs/`logname`', shell=False)


@task
@parallel
@roles('clients')
def clients_pull():
    with show('debug'):
        with cd(env.code_dir_clients):
            run("git pull", shell=False)




@task
@parallel
@roles('clients')
def clients_test():
    with virtualenv_clients():
        run("python requests.py start", shell=False)




@task
@roles('clients')
def check_keys():
    run('cat ~/.ssh/authorized_keys', shell=False)


@task
@roles('clients')
def clients_upload_pubkey(pubkey_file=PUB_KEY):
    with show('debug'):
        with settings(use_ssh_config=False, user='khulan'):
            with settings(warn_only=True):
                if (run("test -d %s" % '/home/khulan/.ssh', shell=False).return_code) == 1:
                    print 'Creating .ssh directory'
                    run("mkdir %s" % '/home/khulan/.ssh', shell=False)
                run("chmod 700 /home/khulan/.ssh", shell=False)
                if (run("test -d %s" % '/home/khulan/.ssh/authorized_keys', shell=False).return_code) == 1:
                    print 'Creating authorized_keys'
                    run("touch %s" %
                        '/home/khulan/.ssh/authorized_keys', shell=False)
                run("chmod 600 /home/khulan/.ssh/authorized_keys", shell=False)
            with open(os.path.expanduser(pubkey_file)) as fd:
                ssh_key = fd.readline().strip()
                run("echo '%s' >> %s" %
                    (ssh_key, '/home/khulan/.ssh/authorized_keys'), shell=False)
                #files.append('/home/khulan/.ssh/authorized_keys', ssh_key, shell=False)


def runbg(cmd):
    run("screen -dmS TTFBclients && sleep 1", shell=False)
    run("screen -S TTFBclients -p 0 -X stuff \"%s\"$(echo -ne '\\015') && sleep 1" %
        cmd, shell=False)


def getCron(path, cmd):
    cd = "cd {} &&".format(path)
    #cron = '*/10 * * * * %s %s'.format(path,cmd)
    cron = '* * * * * {} {}'.format(cd, cmd)
    return cron


def addcrontab(path, cron_cmd):
    cron = getCron(path, cron_cmd)
    run('crontab -l > lastcron; echo \'{}\' >> lastcron; crontab lastcron; rm lastcron'.format(cron), shell=False)


@task
@roles('clients')
def start_experiment():
    if env.host in client_hosts:
        with virtualenv_clients():
            command = "python requests.py start"
            execute(runbg, command)
            execute(addcrontab, env.code_dir_clients, 'bash check_running.sh')


@task
#@parallel
@roles('clients')
def stop_experiment():
    run("crontab -l | grep -v \"check_running.sh\" | crontab -", shell=False)
    with settings(warn_only=True):
        run('screen -S TTFBclients -X quit', shell=False)


@task
@roles('clients')
def check_experiment():
    with settings(warn_only=True):
        run('screen -ls', shell=False)

@task
@roles('clients')
def do_pings():
	with settings(warn_only=True):
		with virtualenv_clients():
			run('python ping.py', shell=False)


@task
@roles('clients')
def get_results():
    if env.host in client_hosts:
        rsync_project(remote_dir=env.code_dir_clients + 'results/',
                      local_dir='./clients/results/', exclude=['log*', '.*'], upload=False)
        print 'Nothing'


@task
@roles('clients')
def get_logs():
    if env.host in client_hosts:
        rsync_project(remote_dir=env.code_dir_clients + 'results/',
                      local_dir='./clients/results/', exclude=['result*', '.*'], upload=False)
    else:
        print 'Nothing'


@task
def check_last_results():
    execute(get_results)
    for directory in ['clients']:
        files = glob.glob('{}/results/results*'.format(directory))
        for fil in files:
            with open(fil, 'r') as f:
                lines = list(f)
                last_timestamp = lines[-1].split(',')[0]
                print '{}: \tLines: {}\tLast Measurement: {}'.format(
                    fil, len(lines), dt.datetime.fromtimestamp(float(last_timestamp)))


@task
def check_logs():
    execute(get_logs)
    for directory in ['clients']:
        files = glob.glob('{}/results/log*'.format(directory))
        for fil in files:
            print "FILE: {}".format(fil)
            with open(fil, 'r') as f:
                for line in list(f):
                    print '\t {}'.format(line)
            print '\n\n'
