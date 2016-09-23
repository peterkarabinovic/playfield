# coding: utf-8

"""
    Скрипт позволяет простматривать растровые файлы в браузере,
    запуская wsgi http server и реализуя компактный TMS сервис.
    Файл перепроецируется в EPSG:3857, затем запускается Flask Web Service
    который обрабатывае z/y/x запорсы, возвращая вырезанный и смаштабированный тайл
"""

from __future__ import print_function

import imp


def check_module(name):
    try:
        imp.find_module(name)
    except ImportError:
        print("Error: '{}' module not installed.\nTry in Anaconda:\n\t$ conda install {}".format(name,name) )
        sys.exit(1)

check_module('numpy')
check_module('osr')
check_module('affine')
check_module('rasterio')
check_module('PIL')
check_module('flask')
check_module('gevent')
check_module('matplotlib')

# from gevent import monkey
# monkey.patch_all()

import os
import sys
import glob
import affine
import rasterio
import numpy as np

###############################################################################
#  Перепроецирование растра если не EPSG:3857
###############################################################################
from rasterio.coords import BoundingBox
from rasterio.warp import reproject, RESAMPLING, calculate_default_transform
import warnings
warnings.filterwarnings("ignore")

def reproject_tif(path):

    with rasterio.Env():
        with rasterio.open(path, 'r') as src:

            if src.crs == {'init': 'epsg:3857'}:
                return path

            name, _ = os.path.splitext(path)
            dst_path = name + "_3857.tif"
            dst_crs = {'init': 'epsg:3857'}

            if os.path.exists(dst_path):
                return dst_path

            dst_transform, dst_width, dst_height = calculate_default_transform(src.crs, dst_crs, src.width, src.height, *src.bounds)
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': dst_crs,
                'transform': dst_transform,
                'affine': dst_transform,
                'width': dst_width,
                'height': dst_height
            })


            dst = np.zeros((src.count, dst_height, dst_width), src.profile['dtype'])

            reproject(
                src.read(),
                dst,
                src_transform=src.affine,
                dst_transform=dst_transform,
                src_crs=src.crs,
                dst_crs=dst_crs,
                resampling=RESAMPLING.nearest)

            with rasterio.open(dst_path, 'w',
                               driver='GTiff',
                               width=dst_width,
                               height=dst_height,
                               count=src.count,
                               dtype=dst.dtype,
                               crs='EPSG:3857',
                               transform=dst_transform,
                               nodata=src.profile['nodata']) as f:
                f.write(dst)

            return dst_path

###############################################################################
#  Web app
###############################################################################
import flask
from gevent import wsgi
import webbrowser
import gevent
from PIL import Image
from io import BytesIO
from rasterio.coords import disjoint_bounds

from matplotlib.cm import ScalarMappable
from matplotlib.colors import SymLogNorm


index_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>${raster_name}</title>
    <link rel="stylesheet" href="http://cdn.leafletjs.com/leaflet-0.7.2/leaflet.css">
    <style type="text/css">
        html, body { height: 100%; margin: 0;}
        #map {min-height: 100%;}
    </style>
</head>
<body>
<div id="map">

<script src="http://cdn.leafletjs.com/leaflet-0.7.2/leaflet.js"></script>
<script type="text/javascript">
    var map = new L.Map('map', {
        center: ${latlng},
        zoom: 5,
        layers : [
            new L.TileLayer('http://tms{s}.visicom.ua/2.0.0/planet3/base_ru/{z}/{x}/{y}.png',{
                    maxZoom : 19,
                    tms : true,
                    attribution : 'Данные компании © <a href="http://visicom.ua/">Визиком</a>',
                    subdomains : '123'
            }),

            new L.TileLayer('http://127.0.0.1:${port}/{z}/{x}/{y}.png',{
                    maxZoom : 19,
                    tms : true
            })
        ]
    });
</script>
</body>
</html>
"""


def run_web(raster_path, host='127.0.0.1', port=5000):

    tms_box = BoundingBox(-20037508.3427892, -20037508.3427808, 20037508.3427892, 20037508.3427807)
    empty_tile = np.zeros((256, 256, 4), dtype='uint8')

    with rasterio.open(raster_path,'r') as raster:

        invert_affine = ~raster.affine
        d = raster.read()
        dtype=raster.profile['dtype']
        vmin, vmax = d.min(), d.max()
        nodata = raster.profile['nodata'] or vmin - 1
        del d

        app = flask.Flask(__name__)

        def tile_affines(tile_box):
            # a = (tile_box.right - tile_box.left) / 256.0  # width of a pixel
            # b = 0  # row rotation (typically zero)
            # c = tile_box.left  # x-coordinate of the upper-left corner of the upper-left pixel
            # d = 0  # column rotation (typically zero)
            # e = - (tile_box.bottom - tile_box.top) / 256.0  # height of a pixel (typically negative)
            # f = tile_box.top # y-coordinate of the of the upper-left corner of the upper-left pixel

            # original_tile_affine
            a1 = raster.affine._replace(c=tile_box.left,
                                        f=tile_box.top)
            # scaled_tile_affine
            a2 = a1._replace(a=(tile_box.right - tile_box.left) / 256.0,
                             e=(tile_box.bottom - tile_box.top) / 256.0)

            return a1, a2




        @app.route('/<int:z>/<int:x>/<int:y>.png')
        def tile(z,x,y):
            step = ( tms_box.right - tms_box.left ) / ( 2 ** z)
            tile_box = BoundingBox(tms_box.left + x * step,
                                    tms_box.bottom + y *step,
                                    tms_box.left + (x + 1)* step,
                                   tms_box.bottom + (y + 1)  * step)
            rgba = empty_tile
            if not disjoint_bounds(raster.bounds,tile_box):
                left_top = invert_affine * (tile_box.left, tile_box.top)
                width = round((tile_box.right - tile_box.left) / raster.affine.a + 0.5)
                height = round((tile_box.bottom - tile_box.top) / raster.affine.e+ 0.5)
                right_bottom = invert_affine * (tile_box.right, tile_box.bottom)
                if round(left_top[0]) < raster.shape[1] and round(left_top[1]) < raster.shape[0]:
                    window = ((left_top[1], left_top[1] + height), (left_top[0], left_top[0]+width))
                    array = raster.read(window=window)
                    src_affine, dest_affine = tile_affines(tile_box)
                    # получаем размеры в гео координатах для вырезаного участка
                    offx, offy = src_affine * array.shape[:0:-1]
                    # из полученых гео координат получаем размер результирующей картинки
                    dest_x, dest_y = ~dest_affine * (offx, offy)
                    dest_array = np.zeros((raster.count, round(dest_y), round(dest_x)), dtype=dtype)
                    # ресайзим вырезанный растр
                    reproject(array,
                              dest_array,
                              src_transform=src_affine,
                              dst_transform=dest_affine)
                    if dest_array.shape[1::] < (256,256):
                        new_dest = np.empty([raster.count,256,256],dtype=dtype)
                        new_dest.fill(nodata)
                        dy,dx = dest_array.shape[1:]
                        new_dest[:,:dy,:dx] = dest_array
                        dest_array = new_dest

                    dest_array = np.ma.masked_values(dest_array, float(nodata), copy=False)



                    if raster.count == 1: # grid with one channel
                        rgba = ScalarMappable(cmap='gist_earth', norm=SymLogNorm(1, vmin=vmin, vmax=vmax, clip=True)).to_rgba(dest_array[0], alpha=0.5)
                        rgba *= 255
                        rgba = np.asarray(rgba, dtype='uint8')
                    elif raster.count == 3: # image with RGB so add A
                        zeros = np.zeros((1, raster.height, raster.width), dtype=int)
                        rgba = np.append( array, zeros, axis=0)


            output = BytesIO()
            Image.fromarray(rgba, mode='RGBA').save(output, 'PNG')
            output.seek(0)
            return flask.send_file(output, mimetype='image/png')


        @app.route('/')
        def index():
            global index_html
            index_html = index_html.replace('${port}', str(port))
            index_html = index_html.replace('${raster_name}', os.path.basename(raster_path))
            index_html = index_html.replace('${latlng}', str(list(raster.lnglat())[::-1]))
            return index_html

        # gevent.spawn(lambda: webbrowser.open(('http://%s:%s') % (host, port)))
        server = wsgi.WSGIServer(('127.0.0.1', port), application=app, log=None)
        server.serve_forever()


###############################################################################
#  Main
###############################################################################
if __name__ == '__main__':

    raster = None
    try:
        if len(sys.argv) > 1:
            path = sys.argv[1]
        else:
            assert len(glob.glob('*.tif')), "no GeoTiff files in current directory"
            path = glob.glob('*.tif')[0]
        assert os.path.exists(path), "file not exists {}".format(path)

        raster_path = reproject_tif(path)
        run_web(raster_path, port=5001)
    except KeyboardInterrupt:
        raster.close()
    except Exception as ex:
        print("Error: {}".format(str(ex)))
