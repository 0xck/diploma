# Device model page
from flask import render_template, request
from app import app
from app.db import Device


@app.route('/device')
def device():
    device_name = request.args.get('device_name').lower()
    device_entr = Device.query.filter(Device.name == device_name).first()
    print(device_name)
    print(device_entr)
    print(device_entr.name)
    print('Device: {0} detail'.format(device_entr.name))
    print(device_entr['ALL_DICT'])
    return render_template(
        'device_unit.html',
        title='Device: {0} detail'.format(device_entr.name),
        page_title='<h1>Device: <i>{0}</i> detail</h1>'.format(device_entr.name),
        content='''
        <p>Uniq id: {id}</p>
        <p>Device name: {name}</p>
        <p><b>Status:</b> {status}</p>
        <hr>
        <p><b>Management</b></p>
        <p>IPv4 address: {ip4}</p>
        <p>IPv6 address: {ip6}</p>
        <p>DNS name: {fqdn}</p>
        <hr>
        <p><i>Hardware</i></p>
        <p>Vendor: {vendor}</p>
        <p>Model: {model}</p>
        <hr>
        <p><i>Firmware</i></p>
        <p>Firmware version: {firmware}</p>
        <hr>
        <p>Device description</p>
        <p>{description}</p>
        '''.format(**device_entr['ALL_DICT']))
