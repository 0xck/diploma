# index page
from flask import redirect
from app import app


@app.route('/')
@app.route('/index')
def index():
    # now here only redirect to tasks page
    return redirect('/tasks')
