#!/usr/bin/env python3

import os
from shutil import which
from sys import exit

term = {
    'red': '\033[91m',
    'grey': '\033[90m',
    'blue': '\033[94m',
    'bold': '\033[01m',
    'end': '\033[0m'
}

supervisor_config = {}
curr_dir = os.getcwd()
conf_file = 'wrex.conf'
app_path = os.path.split(curr_dir)[0]
supervisor_config['server_path'] = os.path.join(app_path, 'server.py')
supervisor_config['task_sched_path'] = os.path.join(app_path, 'task_scheduler.py')
supervisor_config['worker_path'] = os.path.join(app_path, 'worker.py')
supervisor_config['python_path'] = which('python3', mode=os.X_OK)
supervisor_config['redis_path'] = which('redis-server', mode=os.X_OK)
supervisor_config['redis_conf'] = '/etc/redis/redis_supervisor.conf'
supervisor_config['redis_user'] = 'redis'
supervisor_config['app_user'] = os.getlogin()
incl_redis = True


app_part_conf = '''
[program:tasksched]
command={python_path} {task_sched_path}
priority=100
autostart=false
startretries=1
autorestart=unexpected
user={app_user}
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=10
stderr_logfile_maxbytes=10MB
stderr_logfile_backups=10

[program:worker]
command={python_path} {worker_path}
priority=300
autostart=false
startretries=3
autorestart=unexpected
stopasgroup=true
killasgroup=true
user={app_user}
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=10
stderr_logfile_maxbytes=10MB
stderr_logfile_backups=10

[program:server]
command={python_path} {server_path}
priority=200
autostart=false
startretries=3
autorestart=unexpected
stopasgroup=true
user={app_user}
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=10
stderr_logfile_maxbytes=10MB
stderr_logfile_backups=10
'''.format(**supervisor_config)

redis_part_conf = '''
[program:redis]
command={redis_path} {redis_conf}
priority=500
autostart=false
startretries=3
autorestart=unexpected
user={redis_user}
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=10
stderr_logfile_maxbytes=10MB
stderr_logfile_backups=10
'''.format(**supervisor_config)

group_part_conf = '''
[group:wrex]
programs=tasksched,worker,server,redis
'''


def wr_cfg():
    with open(conf_file, 'w', encoding='utf-8') as cfg_file:
        if incl_redis:

            cfg_file.write(app_part_conf + redis_part_conf + group_part_conf)
        else:

            cfg_file.write(app_part_conf + group_part_conf)
    print('''
        Your config has been saved in {bold}{}{end} directory.
        Bye.
        '''.format(curr_dir, **term))


if __name__ == '__main__':
    # welcome
    print('''
        Welcome to {blue}wrex supervisor{end} config generator.
        If you would like create config with default settings just type "y" otherwise interactive setup will be started.
        {grey}Note. Use default settings only in case you exactly know what you are doing.{end}
        '''.format(**term))
    # generating using default
    generate = input('Generate with default settings y/n ')
    if generate.strip().lower() not in {'y', 'n'}:
        while generate.strip().lower() not in {'y', 'n'}:
            generate = input('Please use only {bold}"y"{end} or {bold}"n"{end} '.format(**term))
    # generates and exiting
    if generate.strip().lower() == 'y':
        wr_cfg()
        exit()
    # start interactive
    print('''
        {blue}Interactive setup was started{end}
        Just press "Enter" in case you would like to save suggested value.
        '''.format(**term))
    # app path
    print('Enter full path for application directory')
    user_val = input('{grey}Defaul is current:{end} {bold}{}{end} : '.format(app_path, **term))
    if user_val.strip() != '':
        app_path = user_val
    # app user
    print('Enter name of user for application')
    user_val = input('{grey}Defaul is current user:{end} {bold}{}{end} : '.format(supervisor_config['app_user'], **term))
    if user_val.strip() != '':
        supervisor_config['redis_user'] = user_val
    # python bin
    print('Enter full path for python3 binary')
    user_val = input('{grey}Defaul is current:{end} {bold}{}{end} : '.format(supervisor_config['python_path'], **term))
    if user_val.strip() != '':
        supervisor_config['python_path'] = user_val
    # mng redis with supervisor
    print('Would you like to use supervisor for managing redis startup/shutdown?')
    user_val = input('{grey}Defaul is Yes.{end} Type "n" in case you would not like '.format(**term))
    if user_val.strip().lower() not in {'', 'n'}:
        while user_val.strip().lower() not in {'', 'n'}:
            user_val = input('Please press {bold}"Enter"{end} or type {bold}"n"{end} '.format(**term))
    if user_val.strip().lower() == 'n':
        incl_redis = False
        group_part_conf = '''
[group:wrex]
programs=tasksched,worker,server
'''
    # in case using supervisor for mng redis
    if incl_redis:
        # redis bin
        print('Enter full path for redis server binary')
        user_val = input('{grey}Defaul is :{end} {bold}{}{end} : '.format(supervisor_config['redis_path'], **term))
        if user_val.strip() != '':
            supervisor_config['redis_path'] = user_val
        # redis conf
        print('''
        Enter full path for redis {bold}non demonised{end} config file.
        {grey}In case you do not have this config just create one, copy current redis config and change options{end} {red}daemonize{end} {grey}to{end} {red}no{end}
            '''.format(**term))
        user_val = input('{grey}Defaul is :{end} {bold}{}{end} : '.format(supervisor_config['redis_conf'], **term))
        if user_val.strip() != '':
            supervisor_config['redis_conf'] = user_val
        # redis user
        print('Enter name of user for redis server')
        user_val = input('{grey}Defaul is :{end} {bold}{}{end} : '.format(supervisor_config['redis_user'], **term))
        if user_val.strip() != '':
            supervisor_config['redis_user'] = user_val
    wr_cfg()
