import json
import cPickle


with open('STL1NQ7EP.json', 'r') as f:
    state_json = json.load(f)

with open('STL1NQ7EP.pckl', 'wb') as f:
    cPickle.dump(state_json, f, protocol=2)

with open('STL1NQ7EP.pckl', 'rb') as f:
    state_pckl = cPickle.load(f)    


print type(state_json)
print type(state_pckl)
print state_json == state_pckl
