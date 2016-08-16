import rasterio 
from PIL import Image
from flask import Flask, send_file

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


if __name__ == '__main__':
    
    print "GeoTransform: %s" % repr(dataset.transform)
    print "Affine: %s" % repr(dataset.affine)
    print "Width: %d; Height: %d" % (dataset.width,dataset.height)
    print "Driver: %s" % dataset.driver
    print "RasterCount: %d" % dataset.count

    # app.run(debug=True, host='0.0.0.0')
    dataset.close()

    
