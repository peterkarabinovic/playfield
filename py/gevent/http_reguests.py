

import requests
def no_gevent(number):
    sum = 0;
    for i in xrange(number):
        res = requests.get("http://vdata/analysis/")
        sum += len(res.text)
    return sum

import grequests
def yes_gevent(number):
    urls = ("http://vdata/analysis/" for _ in xrange(number))
    response_futures = (grequests.get(u) for u in urls) #
    responses = grequests.imap(response_futures, size = 100)
    return sum(len(r.text) for r in responses)


import time
t1 = time.time()
print "Sum %d  time %.2f sec" % (no_gevent(1000), time.time() - t1 )
t2 = time.time()
print "Sum %d  time %.2f sec" % (yes_gevent(1000), time.time() - t1 )