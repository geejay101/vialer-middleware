#!/usr/bin/env python2.7

import getpass

import sys
from fabric.api import cd, env, sudo
from fabric.decorators import task

prompt = 'Initial value for env.sudo_password: '
env.sudo_password = getpass.getpass(prompt)


@task()
def prepare(tag, *args, **kwargs):
    with cd('/srv/vialer-middleware'):
        print('Preparing container with tag %s on %s' % (tag, env.host_string))
        output = sudo('./deploy.sh prepare {tag}'.format(tag=tag))
        if 'mysql_health=1' in output and 'redis_health=1' in output:
            print('App server %s has been prepared, MySQL and Redis seem to run.' % env.host_string)
            while True and env.host_string != env.hosts[-1]:
                print('Do you want to continue with the next app server? (y/n)')
                choice = raw_input().lower()
                if choice != 'y':
                    sys.exit()
                break
        else:
            print ('MySQL and Redis are not reachable from the container, '
                   'investigate or rollback to the previous tag.')
            sys.exit()


@task()
def activate(tag, *args, **kwargs):
    with cd('/srv/vialer-middleware'):
        output = sudo('./deploy.sh activate {tag}'.format(tag=tag))
        if 'nginx -s reload' in output:
            print ('App server %s has been activated, nginx has been reloaded.'
                   'Please verify everything is running correctly.') % env.host_string
            while True and env.host_string != env.hosts[-1]:
                print('Do you want to continue with the next app server? (y/n)')
                choice = raw_input().lower()
                if choice != 'y':
                    sys.exit()
                break
        else:
            print('Nginx has not been reloaded, something went wrong. '
                  'Please check the container on %s' % env.host_string)
            sys.exit()


@task()
def staging(*args, **kwargs):
    env.hosts = ['middleapp0-staging.voipgrid.nl', 'middleapp1-staging.voipgrid.nl']


@task()
def production(*args, **kwargs):
    env.hosts = ['middleapp2-ams.voipgrid.nl', 'middleapp2-grq.voipgrid.nl', 'middleapp3-ams.voipgrid.nl']
