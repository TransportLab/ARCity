#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, time, errno, json, logging, jsonify
from flask import Flask, request, send_from_directory
from flask_cors import CORS, cross_origin
from subprocess import call, Popen
import numpy as np
import overpy  # openstreetmap overpass API bindings

app = Flask(__name__)
logging.basicConfig(filename="flask_logfile.log", level=logging.DEBUG)
CORS(app)
# kiosk = True
# depths = np.zeros([25,25])
server_url = "0.0.0.0:5000"
kiosk = False
if kiosk:
    kiosk_string = "--kiosk --disable-pinch --overscroll-history-navigation=0"
else:
    kiosk_string = ""  # "--incognito" # incognito helps with caching

# default value of depths
depths = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 2, 2, 0, 0, 1, 1, 2, 2, 0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 2, 0, 0],
    [0, 0, 1, 1, 2, 2, 0, 0, 1, 1, 2, 2, 0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 2, 0, 0],
    [0, 0, 1, 1, 2, 2, 0, 0, 1, 1, 2, 2, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 4, 4, 4, 4, 0, 0, 2, 2, 3, 3, 0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 2, 0, 0],
    [0, 0, 4, 4, 4, 4, 0, 0, 2, 2, 3, 3, 0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 2, 0, 0],
    [0, 0, 4, 4, 4, 4, 0, 0, 2, 2, 3, 3, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 2, 0, 0],
    [0, 0, 4, 4, 4, 4, 0, 0, 2, 2, 3, 3, 0, 0, 3, 1, 1, 1, 0, 0, 1, 1, 2, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 0, 0, 3, 3, 3, 3, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 0, 0, 3, 3, 3, 3, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 0, 0, 2, 2, 1, 1, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 2, 2, 2, 2, 0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 1, 1, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 2, 2, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 2, 2, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 2, 2, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 2, 2, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

colours = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 2, 2, 0, 0, 1, 1, 2, 2, 0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 2, 0, 0],
    [0, 0, 1, 1, 2, 2, 0, 0, 1, 1, 2, 2, 0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 2, 0, 0],
    [0, 0, 1, 1, 2, 2, 0, 0, 1, 1, 2, 2, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 4, 4, 4, 4, 0, 0, 2, 2, 3, 3, 0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 2, 0, 0],
    [0, 0, 4, 4, 4, 4, 0, 0, 2, 2, 3, 3, 0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 2, 0, 0],
    [0, 0, 4, 4, 4, 4, 0, 0, 2, 2, 3, 3, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 2, 0, 0],
    [0, 0, 4, 4, 4, 4, 0, 0, 2, 2, 3, 3, 0, 0, 3, 1, 1, 1, 0, 0, 1, 1, 2, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 0, 0, 3, 3, 3, 3, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 0, 0, 3, 3, 3, 3, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 0, 0, 2, 2, 1, 1, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 2, 2, 2, 2, 0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 1, 1, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 2, 2, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 2, 2, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 2, 2, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 2, 2, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
# import read_zed
nx = 72
ny = 51
depths = np.zeros([nx, ny]).flatten().tolist()
colours = np.random.rand(nx, ny).flatten().tolist()
colours[depths == 0] = 0
#print(depths.shape, colours.shape)
#print(nx*ny)

@app.route("/")
# def root():
# return app.send_static_file('src/index.html')


@app.route("/<path:path>")
def static_proxy(path):
    print(path)
    # send_static_file will guess the correct MIME type
    # return app.send_static_file(path)
    return send_from_directory("./", path)


# @app.route('/main')
# def main():
#    return 'Up and running'


@app.route("/post_corners_to_server", methods=["POST"])
def post_corners_to_server():
    global corners
    corners = np.array(request.form["corners"])
    # resp = Response(response='Received corners')
    return "Received corners"


@app.route("/get_corners_from_server", methods=["GET"])
def get_corners_to_server():
    # global corners
    return json.dumps(corners)


@app.route("/post_zed_data_to_server", methods=["POST"])
def post_zed_data_to_server():
    global colours
    global depths
    colours = json.loads(request.form["colours"])
    depths = json.loads(request.form["depths"])
    print("Got depths")
    return "Received colours and depths"


@app.route("/get_depths_from_server", methods=["GET"])
def get_depths_from_server():
    global depths
    print("Sent depths")
    return json.dumps(depths)


@app.route("/get_colours_from_server", methods=["GET"])
def get_colours_from_server():
    global colours
    return json.dumps(colours)


@app.route("/post_link_flow", methods=["POST"])
def post_link_flow():
    global flows
    flows = json.loads(request.form["flows"])
    return "Received flows"


@app.route("/get_link_flow", methods=["GET"])
def get_link_flow():
    global flows
    return json.dumps(flows)


@app.route("/get_OSM_links")
def get_OSM_links():
    pass
    # see testing_open_street_map.py for current progress


@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error("Unhandled exception: %s", (e))
    return e


# TO RUN THIS CODE, DO THE FOLLOWING TWO STEPS:
# FLASK_APP=app.py
# flask run

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=1)
    # main()
#    sleep(1)
# main()

# chrome = Popen('/usr/bin/google-chrome ' + kiosk_string + server_url + '/src/index.html', shell=True)
# zed = Popen('/usr/bin/python3 src/read_zed.py', shell=True)
