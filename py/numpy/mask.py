import numpy as np

a = np.ma.masked_values(np.arange(10, 0, -1), 3 )

b = np.ma.masked_array(np.ones(10, dtype=a.dtype), [1,0,0,1,0,0,0,1,0,0] )

# print a.filled(b)
# print a


# print np.ma.concatenate(a,b)
# print b.filled(a)
# print np.ma.getmask(a) ==

# print np.ma.where(a.mask, b, a, mask=np.ma.mask_or(a.mask, b.mask))

print a
print b
print a.mask & b.mask
print np.ma.masked_array( a.filled(0) + b.filled(0), mask=a.mask & b.mask) 



