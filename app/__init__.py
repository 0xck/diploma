# initial app
from flask import Flask

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app config
app.config.from_object('config')
# define db
db = SQLAlchemy(app)

# index; trex instance; device unit
#from app import index, trex_instance, device_unit
