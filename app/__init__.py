# initial flask app
from flask import Flask
# DB
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app config from config.py
app.config.from_object('config')
# defines db
db = SQLAlchemy(app)

# logging func if app is not in debug mode
if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('app/logs/app.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('app startup')

# app pages
from app import index, tasks, tests, trexes, devices
