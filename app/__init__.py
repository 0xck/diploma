# initial app
from flask import Flask

app = Flask(__name__)
# index; trex instance; device unit
from app import index, trex_instance, device_unit
