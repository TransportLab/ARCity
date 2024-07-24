import numpy as np
import matplotlib.pyplot as plt
import requests
import json5

server_url = "http://localhost:5000/"

p = json5.loads(open("../../params.json5", "r").read())
# print(p['colours'][p['corner_colour']]['lower'])

for c in p["colours"]:
    print(c)


def process_colours():
    # Get the data from the API
    r = requests.get(server_url + "get_colours_from_server")
    c = json5.loads(r.text)
