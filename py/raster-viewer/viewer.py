import rasterio 
from PIL import Image
from flask import Flask, send_file
from rasterio.coords import BoundingBox
import osr


"""
    This example from NextGis (http://nextgis.github.io/webgis_course/6/python_gdal.html)
    rewritten with rasterio
"""

dataset = rasterio.open('bathymetry.tif', 'r')
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

    top_left = dataset.affine * ( extent[0], extent(3) )
    bottom_right = dataset.affine * ( extent[2], extent(1) )

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
    
    print "GeoTransform: %s" % repr(dataset.transform)
    print "Affine: \n%s" % str(dataset.affine)
    print "Width: %d; Height: %d" % (dataset.width,dataset.height)
    print "Driver: %s" % dataset.driver
    print "RasterCount: %d" % dataset.count
    print "Bounds: %s" % type(dataset.bounds)
    print "Bounds: %s" % repr(list(dataset.bounds))

    print '(dataset.bounds.right - dataset.bounds.left) / dataset.width =' , (dataset.bounds.right - dataset.bounds.left) / dataset.width


    crs3857 = osr.SpatialReference()
    crs3857.ImportFromEPSG(3857)
    crs4326 = osr.SpatialReference()
    crs4326.ImportFromEPSG(4326)

    _4326_to_3857 = osr.CoordinateTransformation(crs4326, crs3857).TransformPoints
    _3857_to_4326 = osr.CoordinateTransformation(crs3857, crs4326).TransformPoints

    print _4326_to_3857([(0, 0)])


    bounds3857_tms = BoundingBox(-20037508.3427892, -20037508.3427808, 20037508.3427892, 20037508.3427807)
    bounds4326_tms =  _3857_to_4326([bounds3857_tms[:2], bounds3857_tms[2:]])
    bounds4326_tms = BoundingBox(bounds4326_tms[0][0],bounds4326_tms[0][1], bounds4326_tms[1][0],bounds4326_tms[1][1] )

    bounds4326_dst = BoundingBox(dataset.bounds.left,
                                 min(dataset.bounds.bottom, bounds4326_tms.bottom),
                                 dataset.bounds.right,
                                 min(dataset.bounds.top, bounds4326_tms.top))

    bounds3857_dst = _4326_to_3857([bounds4326_dst[:2], bounds4326_dst[2:]])
    bounds3857_dst = BoundingBox(bounds3857_dst[0][0], bounds3857_dst[0][1], bounds3857_dst[1][0], bounds3857_dst[1][1])

    print 'bounds4326_tms', bounds4326_tms
    print 'bounds4326_dst', bounds4326_dst
    print 'bounds3857_dst', bounds3857_dst


    # from rasterio.warp import from_4326_to_3870





    # app.run(debug=True, host='0.0.0.0')
    dataset.close()

    
