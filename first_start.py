#!/usr/bin/env python3

import os
from string import ascii_letters, digits
from random import choice, SystemRandom
from sys import exit
from ext_conf import config_generator


def main_cfg_gen():
    term = {
        'red': '\033[91m',
        'grey': '\033[90m',
        'blue': '\033[94m',
        'bold': '\033[01m',
        'end': '\033[0m'
    }

    conf_file = 'config.py'
    curr_dir = os.getcwd()
    db_addr = 'db.sqlite'
    db_type = 'sqlite'
    db_name = 'wrex'
    db_user = 'wrex'
    db_pass = 'wrex'
    db_port = ''
    #
    redis_addr = 'localhost'
    redis_port = 6379
    redis_url = os.getenv('REDIS_URL', 'redis://{}:{}'.format(redis_addr, redis_port))
    # flask
    app_listen = '0.0.0.0'
    app_port = '5000'
    csrf_key = ''.join(SystemRandom().choice(ascii_letters + digits) for item in range(16))

    db_part_conf = '''SQLALCHEMY_DATABASE_URI = "{}:///{}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
'''.format(db_type, db_addr)
    app_part_conf = '''app_listen = "{}"
app_port = "{}"
CSRF_ENABLED = True
SECRET_KEY = "{}"
'''.format(app_listen, app_port, csrf_key)
    redis_part_conf = '''redis_url = "{}"

'''.format(redis_url)

    def wr_cfg():
        with open(conf_file, 'w', encoding='utf-8') as cfg_file:
            cfg_file.write(db_part_conf + app_part_conf + redis_part_conf)

    # welcome
    print('''
Welcome to {blue}wrex first start{end} config generator.
    If you would like create config with default settings just type "y" otherwise interactive setup will be started.
    {grey}Note. Use default settings only in case you exactly know what you are doing.
    By default SQLite is used as DB, app listens all host addresses on {} port and redis URL is {}.{end}
        '''.format(app_port, redis_url, **term))
    # generating using default
    generate = input('Generate with default settings y/n ')
    if generate.strip().lower() not in {'y', 'n'}:
        while generate.strip().lower() not in {'y', 'n'}:
            generate = input('Please use only {bold}"y"{end} or {bold}"n"{end} '.format(**term))
    # generates and exiting
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
    {grey}3. PostgreSQL is NOT yet supported{end}'''.format(**term))
    user_val = input('{grey}Defaul is{end} {bold}SQLite{end} '.format(**term))
    while user_val.strip().lower() not in '123':
        if user_val.strip().lower() == '':
            break
        user_val = input('Please use only {bold}"1"{end} or {bold}"Enter"{end} '.format(**term))
    if user_val.strip().lower() == '2':
        db_type = 'mysql'
    elif user_val.strip().lower() == '3':
        db_type = 'postgresql'
    else:
        db_type = 'sqlite'
    # DB params
    if db_type != 'sqlite':
        print('''
Select DB address:
{grey}Note. Please, do not specify DB port or credentials here{end}'''.format(**term))
        user_val = input('{grey}Defaul is{end} {bold}{}{end} '.format('localhost', **term))
        if user_val.strip().lower() != '':
            db_addr = user_val
        else:
            db_addr = 'localhost'
            print('''
Select DB name''')
            user_val = input('{grey}Defaul is{end} {bold}{}{end} '.format(db_name, **term))
            if user_val.strip().lower() != '':
                db_name = user_val
            print('''
Select DB port''')
            user_val = input('{grey}Defaul is{end} {bold}{}{end} '.format('3306' if db_type == 'mysql' else '5432', **term))
            if user_val.strip().lower() == '':
                db_port = '3306' if db_type == 'mysql' else '5432'
            else:
                db_port = user_val
            print('''
Specify DB username''')
            user_val = input('{grey}Defaul is{end} {bold}{}{end} '.format(db_name, **term))
            if user_val.strip().lower() != '':
                db_user = user_val
            print('''
Specify DB password''')
            user_val = input('{grey}Defaul is{end} {bold}{}{end} '.format(db_pass, **term))
            if user_val.strip().lower() != '':
                db_pass = user_val
            db_part_conf = '''SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}:{}/{}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
'''.format(db_type, db_user, db_pass, db_addr, db_port, db_name)
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
    print('''
Select addresses which will be listened by web application.
{grey}Note. Use 0.0.0.0 for all addresses on host{end}'''.format(**term))
    user_val = input('{grey}Defaul is{end} {bold}{}{end} '.format(app_listen, **term))
    if user_val.strip().lower() != '':
        app_listen = user_val
    print('''
Select web application port''')
    user_val = input('{grey}Defaul is{end} {bold}{}{end} '.format(app_port, **term))
    if user_val.strip().lower() != '':
        app_port = user_val
        app_part_conf = '''app_listen = "{}"
app_port = "{}"
CSRF_ENABLED = True
SECRET_KEY = "{}"
'''.format(app_listen, app_port, csrf_key)
    # redis params
    print('''
Select redis parameters. Default redis URL is {bold}{}{end}'''.format(redis_url, **term))
    user_val = input('Do defaults suit for you? Type "n" in case you would not like to use defaults ')
    if user_val.strip().lower() not in {'', 'n'}:
        while user_val.strip().lower() not in {'', 'n'}:
            user_val = input('Please press {bold}"Enter"{end} or type {bold}"n"{end} '.format(**term))
    if user_val.strip().lower() == 'n':
        print('''
Select redis address''')
        user_val = input('{grey}Defaul is{end} {bold}{}{end} '.format(redis_addr, **term))
        if user_val.strip().lower() != '':
            redis_addr = user_val
        print('''
Select redis port''')
        user_val = input('{grey}Defaul is{end} {bold}{}{end} '.format(redis_port, **term))
        if user_val.strip().lower() != '':
            redis_port = user_val
        redis_part_conf = '''redis_url = "redis://{}:{}'"

'''.format(redis_addr, redis_port)
    # write config
    wr_cfg()
    print('''
    Main config was generated as {bold}{}{end}
    Now you should generate config for {bold}supervisord{end}.
    {bold}Supervisor config{end} generator is starting.
    '''.format(conf_file, **term))
    config_generator.supervisor_cfg_gen()


if __name__ == '__main__':
    main_cfg_gen()
