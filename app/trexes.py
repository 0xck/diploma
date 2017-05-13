# t-rex model page
from flask import render_template
from app import app, db, models


@app.route('/trexes/')
def tresex_table():
    page_title = 'T-rexes list'

    return render_template('trexes.html', title=page_title)
