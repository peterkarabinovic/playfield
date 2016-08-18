import rasterio 
from PIL import Image
from flask import Flask, send_file
from rasterio.coords import BoundingBox
import osr
import gdal
import numpy as np


"""
    This example from NextGis (http://nextgis.github.io/webgis_course/6/python_gdal.html)
    rewritten with rasterio
"""

src = rasterio.open('bathymetry.tif', 'r')
MAXCOORD = 20037508.34
empty_image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))


app = Flask(__name__)

@app.route('/<z>/<x>/<y>')
def home(z, x, y):
    z, x, y = map(int, (z, x, y))
    
    step = 2 * MAXCOORD / (2 ** z)
    
    # ebvalope of tile in spherical mercator
    extent = (
        - MAXCOORD + x * step, MAXCOORD - (y + 1) * step,
        - MAXCOORD + (x + 1) * step, MAXCOORD - y * step)    

    top_left = src.affine * (extent[0], extent(3))
    bottom_right = src.affine * (extent[2], extent(1))

    width_x = bottom_right[0] - top_left[0]
    width_y = bottom_right[1] - top_left[1]

    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))


class TmsSRS:
    """
        TMS mathematics: tiles, zoom, pixel on zoom .... etc.
    """
    def __init__(self,
                 srid=3857,
                 min_x=-20037508.3427892,
                 min_y=-20037508.3427808,
                 max_x=20037508.3427892,
                 max_y=20037508.3427807,
                 tile_width=256,
                 tile_height=256):

        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.tile_width = tile_width
        self.tile_height = tile_height

        self.srs = osr.SpatialReference()
        self.srs.ImportFromEPSG(srid)

        self.x_zoom_coef = abs(max_x - min_x) / tile_width
        self.y_zoom_coef = abs(max_y - min_y) / tile_height

        wgs_srs = osr.SpatialReference()
        wgs_srs.ImportFromEPSG(4326)
        self.wgs_bounds = osr.CoordinateTransformation(self.srs, wgs_srs).TransformPoints(
            [(self.min_x, self.min_y), (self.max_x, self.max_y)]
        )


    def pixel_size(cls, zoom):
        pixel_width = cls.x_zoom_coef / pow(2, zoom)
        pixel_height = cls.y_zoom_coef / pow(2, zoom)
        return pixel_width, pixel_height



if __name__ == '__main__':
    
    print "GeoTransform: %s" % repr(src.transform)
    print "Affine: \n%s" % str(src.affine)
    print "Width: %d; Height: %d" % (src.width, src.height)
    print "Driver: %s" % src.driver
    print "RasterCount: %d" % src.count
    print "Bounds: %s" % type(src.bounds)
    print "Bounds: %s" % repr(list(src.bounds))

    print '(dataset.bounds.right - dataset.bounds.left) / dataset.width =' , (src.bounds.right - src.bounds.left) / src.width
    print '(dataset.bounds.bottom - dataset.bounds.top) / dataset.height =' , (src.bounds.bottom - src.bounds.top) / src.height

    crs3857 = osr.SpatialReference()
    crs3857.ImportFromEPSG(3857)
    crs4326 = osr.SpatialReference()
    crs4326.ImportFromEPSG(4326)

    _4326_to_3857 = osr.CoordinateTransformation(crs4326, crs3857).TransformPoints
    _3857_to_4326 = osr.CoordinateTransformation(crs3857, crs4326).TransformPoints



    bounds3857_tms = BoundingBox(-20037508.3427892, -20037508.3427808, 20037508.3427892, 20037508.3427807)
    bounds4326_tms =  _3857_to_4326([bounds3857_tms[:2], bounds3857_tms[2:]])
    bounds4326_tms = BoundingBox(bounds4326_tms[0][0],bounds4326_tms[0][1], bounds4326_tms[1][0],bounds4326_tms[1][1] )
    print 'bounds4326_tms', bounds4326_tms

    bounds4326_dst = BoundingBox(src.bounds.left,
                                 max(src.bounds.bottom, bounds4326_tms.bottom),
                                 src.bounds.right,
                                 min(src.bounds.top, bounds4326_tms.top))

    bounds3857_dst = _4326_to_3857([bounds4326_dst[:2], bounds4326_dst[2:]])
    bounds3857_dst = BoundingBox(bounds3857_dst[0][0], bounds3857_dst[0][1], bounds3857_dst[1][0], bounds3857_dst[1][1])

    print 'bounds4326_tms', bounds4326_tms
    print 'bounds3857_dst', bounds3857_dst
    print 'bounds4326_dst', bounds4326_dst
    print 'dataset.bounds', src.bounds

    new_width = (bounds4326_dst.right - bounds4326_dst.left) / (src.bounds.right - src.bounds.left) * src.width
    print new_width

    new_height = round((bounds4326_dst.bottom - bounds4326_dst.top) / (src.bounds.bottom - src.bounds.top) * src.height)
    print new_height

    pixel_size_x = (bounds3857_dst.right - bounds3857_dst.left) / new_width
    pixel_size_y = (bounds3857_dst.bottom - bounds3857_dst.top) / new_height

    print pixel_size_x, pixel_size_y

    dst_transform = [bounds3857_dst.left, pixel_size_x, 0, bounds3857_dst.top, 0, pixel_size_y]

    dst = np.ones((new_width, new_height), src.profile['dtype'])


    def reproject_to_epsg3857(path):
        """
        Reproject dataset to Spherical Mercator
        :param path: path to file
        :return:
        """
        src = gdal.Open(path)
        assert src is not None, "Could not read {}".format(path)
        src_crs = osr.SpatialReference(src.GetProjectionRef())
        src_transform = src.GetGeoTransform()
        src_width, src_height = src.RasterXSize , src.RasterYSize
        pixel_w, pixel_h = src_transform[1], src_transform[5]
        src_left_top  = src_transform[0], src_transform[3]
        src_right_bottom = src_left_top[0] + src_width * pixel_w, src_left_top[1]  + src_height * pixel_h


        # transformatoion function
        crs3857 = osr.SpatialReference()
        crs3857.ImportFromEPSG(3857)
        crs4326 = osr.SpatialReference()
        crs4326.ImportFromEPSG(4326)
        crs4326_to_3857 = osr.CoordinateTransformation(crs4326, crs3857).TransformPoints
        crs3857_to_4326 = osr.CoordinateTransformation(crs3857, crs4326).TransformPoints
        crsSrc_to_4326  = osr.CoordinateTransformation(src_crs, crs4326).TransformPoints

        # transform source conner into wgs
        src_left_top, src_right_bottom = crsSrc_to_4326([src_left_top, src_right_bottom])

        # cut by tms bounds
        tms_top_left = -179.99999999999955, 85.05112877979995
        tms_bottom_right = 179.99999999999955, -85.05112877980004
        src_left_top = src_left_top[0], min(src_left_top[1], tms_top_left[1])
        src_right_bottom = src_right_bottom[0], max(src_right_bottom[1], tms_bottom_right[1])

        # transform into 3857
        dst_left_top, dst_right_bottom = crs4326_to_3857([src_left_top, src_right_bottom])

        tms_min2_x, tms_min2_y, tms_max2_x, tms_max2_y = -20037508.3427892, -20037508.3427808, 20037508.3427892, 20037508.3427807





    reproject_to_epsg3857('bathymetry.tif')
    #
    # from rasterio.warp import reproject, RESAMPLING
    # with rasterio.Env():
    #     reproject(
    #         src.read(),
    #         dst,
    #         src_transform=src.transform,
    #         src_crs=src.crs,
    #         dst_transform=dst_transform,
    #         dst_crs='EPSG:3857',
    #         resampling=RESAMPLING.nearest)
    #

    # with rasterio.open('bathymetry3857.tif', 'w',
    #                    driver='GTiff',
    #                    width=new_width,
    #                    height=new_height,
    #                    count=src.count,
    #                    dtype=src.profile['dtype'],
    #                    crs='EPSG:3857',
    #                    transform=dst_transform,
    #                    nodata=src.profile['nodata']) as f:
    #     f.write(dst)





    # app.run(debug=True, host='0.0.0.0')
    src.close()

    
