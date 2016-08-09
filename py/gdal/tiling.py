# coding: utf-8
from osgeo import gdal
import bisect
import affine

tif_files = ['ukraine-rasters/n49_e040_1arc_v3.tif']

gtif = gdal.Open( tif_files[0] )
transform = gtif.GetGeoTransform()
print 'transform', transform 
pxl_w, pxl_h = transform[1], transform[5]
assert abs(pxl_w) == abs(pxl_h), u'Ячейки должны быть квадратные' 

transform = affine.Affine.from_gdal(*gtif.GetGeoTransform())
print 'Left top',  transform * (0,0)  


upp = [ 156543.0332031,  # units per pixels
        78271.5166016,
        39135.7583008,
        19567.8791504,
        9783.9395752,
        4891.9697876,
        2445.9848938,
        1222.9924469,
        611.4962234,
        305.7481117,
        152.8740559,
        76.4370279,
        38.2185140,
        19.1092570,
        9.5546285,
        4.7773142,
        2.3886571,
        1.1943286,
        0.5971643,
        0.29858215
]
zoom = len(upp) - bisect.bisect_right(upp[::-1],abs(pxl_w)) - 1



