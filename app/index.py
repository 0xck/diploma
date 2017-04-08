# index page
from flask import render_template
from app import app


@app.route('/')
@app.route('/index')
def index():
    return render_template(
        'index.html',
        title='W-rex main',
        content='''
        <h1>Welcome to W-rex</h1>
        <p style="color: #9E9E9E">Cisco T-rex web interface</p>''')
