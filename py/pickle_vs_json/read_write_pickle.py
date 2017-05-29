import timeit

s = '''\
import cPickle

with open('STL1NQ7EP.pckl', 'rb') as f:
    state_pckl = cPickle.load(f)

with open('STL1NQ7EP-copy.pckl', 'wb') as f:
    cPickle.dump(state_pckl, f, protocol=cPickle.HIGHEST_PROTOCOL)
'''

print timeit.timeit(stmt=s, number=1000)