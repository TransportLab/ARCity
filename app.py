#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, time, errno, json, logging
from flask import Flask, request
from flask_cors import CORS, cross_origin
from subprocess import call, Popen
import numpy as np

app = Flask(__name__)
logging.basicConfig(filename='flask_logfile.log',level=logging.DEBUG)
CORS(app)
kiosk = True

#kiosk = False
if kiosk:
    kiosk_string = "--kiosk --disable-pinch --overscroll-history-navigation=0"
else:
    kiosk_string = ""

@app.route('/')

@app.route('/main', methods=['POST'])
def main():
    chrome = Popen('/usr/bin/google-chrome ' + kiosk_string + '/index.html', shell=True)
    zed = Popen('/usr/bin/python3 src/read_zed.py', shell=True)
    return 'Up and running'


@app.route('/post_corners_to_server', methods=['POST'])
def send_corners_to_server():
    corners = np.array(request.form['corners'])
    resp = Response(response='Received corners')
    return resp

@app.route('/get_corners_from_server', methods=['GET'])
def get_corners_to_server():
    return json.dumps(corners)


@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error('Unhandled exception: %s', (e))
    return 'ERROR!'

# TO RUN THIS CODE, DO THE FOLLOWING TWO STEPS:
# FLASK_APP=server.py
# flask run

#if __name__ == '__main__':
#app.run()
#    sleep(1)
main()
