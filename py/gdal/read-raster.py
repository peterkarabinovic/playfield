from osgeo import gdal
from fp import Stream
import glob

def log(*arg):
    msg = ' '.join(map(str,arg))
    print msg

files = glob.glob('D:/source/visicom/vdata/bin/tools/*.tif')
files = ['ukraine-rasters/n50_utm36n.tif']


for rater_path in files:
    gtif = gdal.Open( rater_path )

    # Get Raster Metadata
    print '-'*10 + rater_path + '-'*10 
    print gtif.GetMetadata()
    print "band count = ", gtif.RasterCount
    print "size = ", gtif.RasterXSize, 'x', gtif.RasterYSize
    # print 'projection: ', gtif.GetProjectionRef()
    transform = gtif.GetGeoTransform()
    print 'transform: ', transform
    print 'pixel size: ', transform[1], 'x', transform[5]

    def band_stats(band):
        s = band.GetStatistics(True, True)
        log( "\tstat: Min=%.3f, Max=%.3f, Mean=%.3f, StdDev=%.3f" % (s[0],s[1],s[2],s[3]))

    def band_params(band):
        log('\tno_data_val=', band.GetNoDataValue())    
        log('\tscale=', band.GetScale())    
        log('\tunit_type=', gdal.GetDataTypeName(band.DataType))
        log('\tcolor_table=', band.GetColorTable())    


    Stream(range(gtif.RasterCount)) \
            .oneach(lambda i: log('band #',i+1,':'))\
            .map(lambda i: gtif.GetRasterBand(i+1)) \
            .oneach(band_stats) \
            .oneach(band_params) \
            .list()
