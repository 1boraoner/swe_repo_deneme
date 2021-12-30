from requests import get
import json

URL = 'http://127.0.0.1:5000/get_graph_data'
PARAMS = {'Initiator': "requester9000"}

r = get(url=URL, params=PARAMS)
data = (r.json)
print(data)
