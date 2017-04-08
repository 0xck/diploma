# initial app
from flask import Flask

app = Flask(__name__)
# index page
from app import index
# trex instance page
from app import trex_instance
