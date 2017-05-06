import os
# DB conf
SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = False
# redis
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
# flask
app_listen = '0.0.0.0'
app_port = '5000'
