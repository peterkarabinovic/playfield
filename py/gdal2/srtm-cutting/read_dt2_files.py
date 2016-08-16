import os
import glob

import gdal
import gdalnumeric


def readfile(src):
    arr = gdalnumeric.LoadFile(src)
    print arr

path = "D:\data\srtm3"

files = glob.iglob(path + "\*.dt2")
for f in files:
    readfile(f)



