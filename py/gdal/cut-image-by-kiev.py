# coding=utf-8
import urllib2
import json
import sys
from timeit import default_timer as timer
from osgeo import ogr, osr, gdal, gdalnumeric
from PIL import Image, ImageDraw
from fp import Stream


raster_path = "vgrids/n50_e030_1arc_v3.tif"

def world2pixel(matrix, x,y):
    """
    Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
    the pixel location of a geospatial coordinate
    """
    pixel = int((x - matrix[0]) / matrix[1])
    line = int((matrix[3] - y) / matrix[1])
    return (pixel, line)    

# загружаем как numpy.array
t1 = timer()
array = gdalnumeric.LoadFile(raster_path)
print 'Loading image of %d bytes in %.3f sec' % (sys.getsizeof(array), timer() - t1)

# получаем geotransform
geotiff = gdal.Open(raster_path)
transform = geotiff.GetGeoTransform()
raster_proj = osr.SpatialReference(gdal.Open(raster_path).GetProjectionRef())

geojson = urllib2.urlopen("http://api.visicom.ua/data-api/2.0/ru/feature/STL1NQ7EP.json?key=5a7fc7cf6178483d6c40687c237f5785").read()
kiev = ogr.CreateGeometryFromJson( json.dumps( json.loads(geojson)['geometry'] ) )

# reproject Kiev
t1 = timer()
kiev_proj = kiev.GetSpatialReference()
proj_transform = osr.CoordinateTransformation(kiev_proj, raster_proj)
kiev.Transform(proj_transform)
print 'Reproject Kiev in %.3f sec' % (timer() - t1)


minX, maxX, minY, maxY = kiev.GetEnvelope()
print minX, maxX, minY, maxY
ulX, ulY = world2pixel(transform, minX, maxY)
lrX, lrY = world2pixel(transform, maxX, minY)
pxWidth = int(lrX - ulX)
pxHeight = int(lrY - ulY)

print pxWidth, pxHeight

# вырезаем 
clip = array[ulY:lrY, ulX:lrX]

transform = list(transform)
transform[0] = minX
transform[3] = maxY


# рисуем киев на image чтобы сделать mask
t1 = timer()
points = []
pixels = []
kiev_points = kiev.GetGeometryRef(0)
pixels = Stream(range(kiev_points.GetPointCount())) \
                .map( lambda i: (kiev_points.GetX(i), kiev_points.GetY(i)) ) \
                .map( lambda x, y: world2pixel(transform, x,y) ).list()

rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
rasterize = ImageDraw.Draw(rasterPoly)
rasterize.polygon(pixels, 0)


mask = gdalnumeric.fromstring(rasterPoly.tobytes(),'b')
mask.shape=rasterPoly.im.size[1], rasterPoly.im.size[0]

print "Create mask %.3f sec" % (timer() - t1)

# Clip the image using the mask
clip = gdalnumeric.choose(mask, (clip, 0)).astype(gdalnumeric.uint16)
gdalnumeric.SaveArray(clip, "kiev.tif", format="GTiff", prototype=raster_path)


dataset = gdal.GetDriverByName('GTiff')\
              .Create('kiev2.tif', pxWidth, pxHeight, 1, gdal.GDT_Byte)


dataset.SetGeoTransform(transform)
dataset.SetProjection(str(raster_proj))
print 'GetBlockSize()', dataset.GetRasterBand(1).GetBlockSize()
dataset.GetRasterBand(1).SetNoDataValue(0);
dataset.GetRasterBand(1).WriteArray(clip)
dataset.FlushCache()

clip = clip.astype(gdalnumeric.uint8)
gdalnumeric.SaveArray(clip, "kiev.jpg", format="JPEG")
