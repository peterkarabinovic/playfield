
import glob
import os
from utils import *
from multiprocessing.pool import ThreadPool, Pool

files =  (listTree("D:\\dev-tools"))
files = (filter( lambda f: len(f) < 260, files))


def fsize(f):
    return os.stat(f).st_size

@timing
def sequenceCalc(files):
    return sum([fsize(f) for f in files])

@timing
def threadCalc(files):
    pool = ThreadPool(10)
    size = pool.map(fsize, files)
    return sum(size)

@timing
def processCals(files):
    pool = Pool(5)
    size = pool.map(fsize, files)
    return sum(size)


if __name__ == '__main__1':
    print( (sequenceCalc(files)) )
    print( (threadCalc(files)) )
    print( (processCals(files)) )



pool = ThreadPool(10)

def p(x):
    print 'p',x

pool.spawn(p,range(0,10))



