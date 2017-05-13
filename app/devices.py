# t-rex model page
from flask import render_template
from app import app, db, models


@app.route('/devices/')
def devices_table():
    page_title = 'Devices list'

    return render_template('devices.html', title=page_title)
