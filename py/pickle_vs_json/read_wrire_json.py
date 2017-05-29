import timeit

s = """\
import json

with open('STL1NQ7EP.json', 'rb') as f:
    state_json = json.load(f)

with open('STL1NQ7EP-copy.json', 'wb') as f:
    json.dump(state_json, f)
"""

print timeit.timeit(stmt=s, number=1000)