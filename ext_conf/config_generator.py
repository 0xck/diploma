#!/usr/bin/env python3

import os
from shutil import which
from sys import exit


def supervisor_cfg_gen():
    # terminal formatting
    term = {
        'red': '\033[91m',
        'grey': '\033[90m',
        'blue': '\033[94m',
        'bold': '\033[01m',
        'end': '\033[0m'
    }
    # vars
    curr_dir = os.getcwd()
    conf_file = 'wrex.conf'
    # in case script is started from first_start.py
    if os.path.split(curr_dir)[1] != 'ext_conf':
        app_path = curr_dir
        curr_dir = os.path.join(curr_dir, 'ext_conf')
        conf_file = os.path.join(curr_dir, conf_file)
    else:
        app_path = os.path.split(curr_dir)[0]
    incl_redis = True
    supervisor_config = {
        'server_path': os.path.join(app_path, 'server.py'),
        'server_dir': app_path,
        'task_sched_path': os.path.join(app_path, 'task_scheduler.py'),
        'task_sched_dir': app_path,
        'worker_path': os.path.join(app_path, 'worker.py'),
        'worker_dir': app_path,
        'python_path': 'python3' if which('python3', mode=os.X_OK) is None else which('python3'),
        'redis_path': 'redis-server' if which('redis-server', mode=os.X_OK) is None else which('redis-server'),
        'redis_conf': '/etc/redis/redis_supervisor.conf',
        'redis_user': 'redis',
        'app_user': os.getlogin()
    }

    app_part_conf = '''[program:tasksched]
command={python_path} {task_sched_path}
directory={task_sched_dir}
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
directory={worker_dir}
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
directory={server_dir}
priority=200
autostart=false
startretries=3
autorestart=unexpected
stopasgroup=true
user={app_user}
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=10
stderr_logfile_maxbytes=10MB
stderr_logfile_backups=10'''.format(**supervisor_config)

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
stderr_logfile_backups=10'''.format(**supervisor_config)

    group_part_conf = '''

[group:wrex]
programs=tasksched,worker,server,redis
'''

    def wr_cfg():
        # writes config file
        with open(conf_file, 'w', encoding='utf-8') as cfg_file:
            # if redis is managed by supervisor
            if incl_redis:
                cfg_file.write(app_part_conf + redis_part_conf + group_part_conf)
            # redis is not managed by supervisor
            else:
                cfg_file.write(app_part_conf + group_part_conf)
        print('''
Your config has been saved in {bold}{}{end} directory.
    Bye.
            '''.format(curr_dir, **term))

    # welcome msg
    print('''
Welcome to {blue}wrex supervisor{end} config generator.
    If you would like create config with default settings just type "y" otherwise interactive setup will be started.
    {grey}Note. Use default settings only in case you exactly know what you are doing.
    By default all components are managed by supervisord. Information about components is got from system environment and current application directory.{end}
        '''.format(**term))
    # generating using default
    generate = input('Generate with default settings y/n ')
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
    if user_val.strip().lower() != '':
        app_path = user_val
    # app user
    print('''
Enter name of user for application''')
    user_val = input('{grey}Defaul is current user:{end} {bold}{}{end} : '.format(supervisor_config['app_user'], **term))
    if user_val.strip().lower() != '':
        supervisor_config['redis_user'] = user_val
    # python bin
    print('''
Enter full path for python3 binary''')
    user_val = input('{grey}Defaul is current:{end} {bold}{}{end} : '.format('Has not found in system!'if supervisor_config['python_path'] == 'python3' else supervisor_config['python_path'], **term))
    if user_val.strip().lower() != '':
        supervisor_config['python_path'] = user_val
    # mng redis with supervisor
    print('''
Would you like to use supervisor for managing redis startup/shutdown?''')
    user_val = input('{grey}Defaul is Yes.{end} Type "n" in case you would like to manage redis without supervisord '.format(**term))
    if user_val.strip().lower() not in {'', 'n'}:
        while user_val.strip().lower() not in {'', 'n'}:
            user_val = input('Please press {bold}"Enter"{end} or type {bold}"n"{end} '.format(**term))
    if user_val.strip().lower() == 'n':
        incl_redis = False
        group_part_conf = '''[group:wrex]
programs=tasksched,worker,server'''
    # in case using supervisor for mng redis
    if incl_redis:
        # redis bin
        print('''
Enter full path for redis server binary''')
        user_val = input('{grey}Defaul is :{end} {bold}{}{end} : '.format('Has not found in system!' if supervisor_config['redis_path'] == 'redis-server' else supervisor_config['redis_path'], **term))
        if user_val.strip().lower() != '':
            supervisor_config['redis_path'] = user_val
        # redis conf
        print('''
Enter full path for redis {bold}non demonised{end} config file.
{grey}In case you do not have this config just create one, copy current redis config and change options{end} {red}daemonize{end} {grey}to{end} {red}no{end}
            '''.format(**term))
        user_val = input('{grey}Defaul is :{end} {bold}{}{end} : '.format(supervisor_config['redis_conf'], **term))
        if user_val.strip().lower() != '':
            supervisor_config['redis_conf'] = user_val
        # redis user
        print('''
Enter name of user for redis server''')
        user_val = input('{grey}Defaul is :{end} {bold}{}{end} : '.format(supervisor_config['redis_user'], **term))
        if user_val.strip().lower() != '':
            supervisor_config['redis_user'] = user_val
    wr_cfg()


if __name__ == '__main__':
    supervisor_cfg_gen()
