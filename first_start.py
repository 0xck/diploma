#!/usr/bin/env python3

# config generator
# sys
import os
from sys import exit
# for key generation
from string import ascii_letters, digits
from random import choice, SystemRandom
# supervisor config generator
from ext_conf import config_generator


def main_cfg_gen():
    # terminal formatting
    term = {
        'red': '\033[91m',
        'grey': '\033[90m',
        'blue': '\033[94m',
        'bold': '\033[01m',
        'end': '\033[0m'
    }

    conf_file = 'config.py'
    curr_dir = os.getcwd()
    # DB
    db_addr = 'db.sqlite'
    db_type = 'sqlite'
    db_name = 'wrex'
    db_user = 'wrex'
    db_pass = 'wrex'
    db_port = ''
    # redis
    redis_addr = 'localhost'
    redis_port = 6379
    redis_url = os.getenv('REDIS_URL', 'redis://{}:{}'.format(redis_addr, redis_port))
    # flask
    app_listen = '0.0.0.0'
    app_port = 5000
    csrf_key = ''.join(SystemRandom().choice(ascii_letters + digits) for item in range(16))
    app_log_file = os.path.join(curr_dir, './app/logs/app.log')
    # task scheduler
    task_sched_interval = 300
    task_sched_safe = 600

    db_part_conf = '''SQLALCHEMY_DATABASE_URI = "{}:///{}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
'''.format(db_type, db_addr)
    app_part_conf = '''app_listen = "{}"
app_port = {}
CSRF_ENABLED = True
SECRET_KEY = "{}"
'''.format(app_listen, app_port, csrf_key)
    redis_part_conf = '''redis_url = "{}"
'''.format(redis_url)
    task_shed_part_conf = '''task_sched_interval = {}
task_sched_safe = {}
'''.format(task_sched_interval, task_sched_safe)

    def sqlite_create():
        # creates sqlite DB
        # cheking path
        if db_addr == 'db.sqlite':
            # adding full path
            full_db_addr = os.path.join(curr_dir, 'app', db_addr)
        # if user setuped path to DB
        else:
            full_db_addr = db_addr
        # checking if DB exists and rewrites one
        if os.access(full_db_addr, mode=os.F_OK):
            print('''
SQLite DB file {bold}{}{end} already exists, should {red}replace{end} it?
'''.format(full_db_addr, **term))
            rewrite = input('Replace y/n ')
            while rewrite.strip().lower() not in {'y', 'n'}:
                rewrite = input('Please use only {bold}"y"{end} or {bold}"n"{end} '.format(**term))
            if rewrite.strip().lower() == 'y':
                # removes old DB
                if os.access(full_db_addr, mode=os.W_OK):
                    os.remove(full_db_addr)
                    # create DB file and metadata
                    from app import db
                    db.create_all()
                    print('DB {bold}{}{end} was replased '.format(full_db_addr, **term))
                else:
                    print('DB {bold}{}{end} can not be replased. {bold}No permissions{end}'.format(full_db_addr, **term))
        # create DB file and metadata
        else:
            from app import db
            db.create_all()
            print('New DB was created as {bold}{}{end}'.format(full_db_addr, **term))

    def wr_cfg():
        # writes config file
        with open(conf_file, 'w', encoding='utf-8') as cfg_file:
            cfg_file.write(db_part_conf + app_part_conf + task_shed_part_conf + redis_part_conf)
        # creating app.log file
        if not os.access(app_log_file, mode=os.F_OK):
            try:
                os.mkdir(os.path.split(app_log_file)[0])
            except OSError:
                pass
            with open(app_log_file, 'w', encoding='utf-8') as log_file:
                log_file.write('app.log was created')
        # trying to create sqlite DB
        if db_type == 'sqlite':
            sqlite_create()

    # welcome
    print('''
Welcome to {blue}wrex first start{end} config generator.
    If you would like create config with default settings just type "y" otherwise interactive setup will be started.
    {grey}Note. Use default settings only in case you exactly know what you are doing.
    By default SQLite is used as DB, app listens all host addresses on {} port and redis URL is {}. Web app listens all addresses and uses {} port. Task scheduler checks for new tasks every {} seconds.{end}
        '''.format(app_port, redis_url, app_port, task_sched_interval, **term))
    # generating using default values
    generate = input('Generate with default settings y/n ')
    if generate.strip().lower() not in {'y', 'n'}:
        while generate.strip().lower() not in {'y', 'n'}:
            generate = input('Please use only {bold}"y"{end} or {bold}"n"{end} '.format(**term))
    # generates and starts supervisor config generator
    if generate.strip().lower() == 'y':
        wr_cfg()
        print('''
Main config was generated as {bold}{}{end}
    Now you should generate config for {bold}supervisord{end}.
    {bold}Supervisor config{end} generator is starting.
        '''.format(conf_file, **term))
        config_generator.supervisor_cfg_gen()
        exit()
    # start interactive
    print('''
{blue}Interactive setup was started{end}
    Just press "Enter" in case you would like to save suggested value.
        '''.format(**term))
    # DB type
    print('''Choose application DB type:
    1. SQLite {grey}(default){end}
    {grey}2. MySQL is NOT yet supported{end}
    {grey}3. PostgreSQL is NOT yet supported{end}
'''.format(**term))
    user_val = input('{grey}Defaul is{end} {bold}SQLite{end} '.format(**term))
    while user_val.strip().lower() not in {'1', '2', '3'}:
        if user_val.strip().lower() == '':
            break
        user_val = input('Please use only {bold}"1"{end} or {bold}"Enter"{end} '.format(**term))
    if user_val.strip().lower() == '2':
        db_type = 'mysql'
    elif user_val.strip().lower() == '3':
        db_type = 'postgresql'
    else:
        db_type = 'sqlite'
    # DB params in case no sqlite
    if db_type != 'sqlite':
        # DB address
        print('''
Select DB address:
{grey}Note. Please, do not specify DB port or credentials here{end}'''.format(**term))
        user_val = input('{grey}Defaul is{end} {bold}{}{end} '.format('localhost', **term))
        if user_val.strip().lower() != '':
            db_addr = user_val
        else:
            db_addr = 'localhost'
            # DB name
            print('''
Select DB name''')
            user_val = input('{grey}Defaul is{end} {bold}{}{end} '.format(db_name, **term))
            if user_val.strip().lower() != '':
                db_name = user_val
            # DB port
            print('''
Select DB port''')
            sw = True
            while sw is True:
                user_val = input('{grey}Defaul is{end} {bold}{}{end} '.format('3306' if db_type == 'mysql' else '5432', **term))
                if user_val.strip().lower() != '':
                    try:
                        if 0 < int(user_val.strip()) < 65536:
                            db_port = int(user_val)
                            sw = False
                        else:
                            print('Wrong port, try again.')
                    except ValueError:
                        print('Wrong port, try again.')
                        continue
                else:
                    db_port = 3306 if db_type == 'mysql' else 5432
                    sw = False
            # DB username
            print('''
Specify DB username''')
            user_val = input('{grey}Defaul is{end} {bold}{}{end} '.format(db_name, **term))
            if user_val.strip().lower() != '':
                db_user = user_val
            # DB password
            print('''
Specify DB password''')
            user_val = input('{grey}Defaul is{end} {bold}{}{end} '.format(db_pass, **term))
            if user_val.strip().lower() != '':
                db_pass = user_val
            # making changes in defaults
            db_part_conf = '''SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}:{}/{}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
'''.format(db_type, db_user, db_pass, db_addr, db_port, db_name)
    # if DB is sqlite
    else:
        # DB location
        print('''
Select SQLite DB file name with full path''')
        user_val = input('{grey}Defaul DB is in "app" directory:{end} {bold}{}{end} '.format(os.path.join(curr_dir, 'app', db_addr), **term))
        if user_val.strip().lower() != '':
            db_addr = user_val
            db_part_conf = '''SQLALCHEMY_DATABASE_URI = "{}:///{}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
'''.format(db_type, db_addr)
    # app params
    # listened addresses
    print('''
Select addresses which will be listened by web application.
{grey}Note. Use 0.0.0.0 for all addresses on host{end}'''.format(**term))
    user_val = input('{grey}Defaul is{end} {bold}{}{end} '.format(app_listen, **term))
    if user_val.strip().lower() != '':
        app_listen = user_val
    # app port
    print('''
Select web application port''')
    sw = True
    while sw is True:
        user_val = input('{grey}Defaul is{end} {bold}{}{end} '.format(app_port, **term))
        if user_val.strip().lower() != '':
            try:
                if 0 < int(user_val.strip()) < 65536:
                    app_port = int(user_val)
                    app_part_conf = '''app_listen = "{}"
    app_port = {}
    CSRF_ENABLED = True
    SECRET_KEY = "{}"'''.format(app_listen, app_port, csrf_key)
                    sw = False
                else:
                    print('Wrong port, try again.')
            except ValueError:
                print('Wrong port, try again.')
                continue
        else:
            sw = False
    # task scheduler time interval
    print('''
Select time interval which will be used by task scheduler for checking new tasks.
'{grey}Note. Do not set too low interval, task sheduller uses DB for checking new tasks, if interval is small it may affect DB performance.{end}'''.format(**term))
    sw = True
    while sw is True:
        user_val = input('{grey}Defaul is{end} {bold}{}{end}{grey} seconds. And must be{end} {bold}{}{end} {grey}or more.{end} '.format(task_sched_interval, 1, **term))
        if user_val.strip().lower() != '':
            try:
                if int(user_val.strip()) >= 1:
                    task_sched_interval = int(user_val)
                    sw = False
                else:
                    print('Wrong time interval, try again.')
            except ValueError:
                print('Wrong time interval, try again.')
                continue
        else:
            sw = False
    # redis params
    print('''
Select redis parameters. Default redis URL is {bold}{}{end}'''.format(redis_url, **term))
    user_val = input('Do defaults suit for you? Type "n" in case you would not like to use defaults ')
    if user_val.strip().lower() not in {'', 'n'}:
        while user_val.strip().lower() not in {'', 'n'}:
            user_val = input('Please press {bold}"Enter"{end} or type {bold}"n"{end} '.format(**term))
    if user_val.strip().lower() == 'n':
        # redis address
        print('''
Select redis address''')
        user_val = input('{grey}Defaul is{end} {bold}{}{end} '.format(redis_addr, **term))
        if user_val.strip().lower() != '':
            redis_addr = user_val
        # redis port
        print('''
Select redis port''')
        sw = True
        while sw is True:
            user_val = input('{grey}Defaul is{end} {bold}{}{end} '.format(redis_port, **term))
            if user_val.strip().lower() != '':
                try:
                    if 0 < int(user_val.strip()) < 65536:
                        redis_port = int(user_val)
                        redis_part_conf = '''redis_url = "redis://{}:{}'"

'''.format(redis_addr, redis_port)
                        sw = False
                    else:
                        print('Wrong port, try again.')
                except ValueError:
                    print('Wrong port, try again.')
                    continue
            else:
                sw = False
    # writes config and starts supervisor config generator
    wr_cfg()
    print('''
Main config was generated as {bold}{}{end}
'''.format(conf_file, **term))
    print('''Now you should generate config for {bold}supervisord{end}.
    {bold}Supervisor config{end} generator is starting.'''.format(conf_file, **term))
    config_generator.supervisor_cfg_gen()


if __name__ == '__main__':
    main_cfg_gen()
