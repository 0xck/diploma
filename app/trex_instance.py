# t-rex model page
from flask import render_template, request
from app import app
from app.db import Trex


@app.route('/trex')
def trex():
    trex_name = request.args.get('trex_name').lower()
    trex_entr = Trex.query.filter(Trex.hostname == trex_name).first()
    print(trex_name)
    print(trex_entr)
    print(trex_entr.hostname)
    print('T-rex: {0} detail'.format(trex_entr.hostname))
    print(trex_entr['ALL_DICT'])
    return render_template(
        'trex_instance.html',
        title='T-rex: {0} detail'.format(trex_entr.hostname),
        page_title='T-rex: {0} detail'.format(trex_entr.hostname),
        content='''
        <p>Uniq id: {id}</p>
        <p>Hostname: {hostname}</p>
        <p>Server mode: {mode}</p>
        <p><b>Status:</b> {status}</p>
        <hr>
        <p><i>Software</i></p>
        <p>Software version: {version}</p>
        <hr>
        <p><b>Management</b></p>
        <p>IPv4 address: {ip4}</p>
        <p>IPv6 address: {ip6}</p>
        <p>DNS name: {fqdn}</p>
        <p>Port: {port}</p>
        <hr>
        <p><b>VM settings</b></p>
        <p>Host: {host}</p>
        <p>VM id: {vm_id}</p>
        <hr>
        <p>T-rex description</p>
        <p>{description}</p>
        '''.format(**trex_entr['ALL_DICT']))
