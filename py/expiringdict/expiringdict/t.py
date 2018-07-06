from expiringdict import ExpiringDict
import time

cache = ExpiringDict(max_len=2, max_age_seconds=3)

cache['key'] = True
print cache.get('key')
print cache.get('key')
print cache.get('key')
time.sleep(2)
print 'time.sleep(2)', cache.get('key')
cache['key'] = cache.get('key')
time.sleep(2)
print 'time.sleep(2)', cache.get('key')
