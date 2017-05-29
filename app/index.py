# index page
from flask import redirect
from app import app


@app.route('/')
@app.route('/index')
def index():
    return redirect('/tasks')
