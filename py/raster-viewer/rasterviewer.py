# coding: utf-8

"""
    Скрипт позволяет простматривать растровые файлы в браузере,
    запуская wsgi http server и реализуя компактный TMS сервис.
    Файл перепроецируется в EPSG:3857, затем запускается Flask Web Service
    который обрабатывае z/y/x запорсы, возвращая вырезанный и смаштабированный тайл
"""

from __future__ import print_function

import imp
import multiprocessing
import webbrowser
import math


def check_module(name):
    try:
        imp.find_module(name)
    except ImportError:
        print("Error: '{}' module not installed.\nTry in Anaconda:\n\t$ conda install {}".format(name,name) )
        sys.exit(1)

check_module('numpy')
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
import rasterio
import numpy as np
import gevent

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
from PIL import Image
from io import BytesIO
from rasterio.coords import disjoint_bounds
from rasterio.plot import reshape_as_image
from matplotlib.cm import ScalarMappable
from matplotlib.colors import SymLogNorm



def run_index_webserver(raster_path, lnglat, zoom, host, port):

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
            zoom: ${zoom},
            layers : [
                new L.TileLayer('http://tms{s}.visicom.ua/2.0.0/planet3/base_ru/{z}/{x}/{y}.png',{
                        maxZoom : 19,
                        tms : true,
                        attribution : 'Данные компании © <a href="http://visicom.ua/">Визиком</a>',
                        subdomains : '123'
                }),

                new L.TileLayer('http://${host}:${port}{s}/{z}/{x}/{y}.png',{
                        maxZoom : 19,
                        tms : true,
                        subdomains : '123'
                })
            ]
        });
    </script>
    </body>
    </html>
    """

    app = flask.Flask(__name__ + "_index")

    @app.route('/')
    def index():
        html = index_html
        html = html.replace('${host}', host)
        html = html.replace('${port}', str(port)[:-1])
        html = html.replace('${raster_name}', os.path.basename(raster_path))
        html = html.replace('${latlng}', str(list(lnglat)[::-1]))
        html = html.replace('${zoom}', str(zoom))
        return html

    gevent.spawn(lambda: webbrowser.open('http://{}:{}'.format(host, port)))
    server = wsgi.WSGIServer((host, port), application=app, log=None)
    server.serve_forever()


def run_title_webserver(raster_path, vmin, vmax, host, port):

    tms_box = BoundingBox(-20037508.3427892, -20037508.3427808, 20037508.3427892, 20037508.3427807)
    empty_tile = np.zeros((256, 256, 4), dtype='uint8')

    with rasterio.open(raster_path, 'r') as raster:
        invert_affine = ~raster.affine
        dtype=raster.profile['dtype']
        nodata = raster.profile['nodata']

        app = flask.Flask(__name__)

        def tile_affines(tile_box):
            # a = (tile_box.right - tile_box.left) / 256.0  # width of a pixel
            # b = 0  # row rotation (typically zero)
            # c = tile_box.left  # x-coordinate of the upper-left corner of the upper-left pixel
            # d = 0  # column rotation (typically zero)
            # e = - (tile_box.bottom - tile_box.top) / 256.0  # height of a pixel (typically negative)
            # f = tile_box.top # y-coordinate of the of the upper-left corner of the upper-left pixel

            # original_tile_affine
            left = max(raster.affine.c , tile_box.left)
            top = min(raster.affine.f, tile_box.top)
            src = raster.affine._replace(c=left,
                                        f=top)
            # scaled_tile_affine
            dest = src._replace(c=tile_box.left,
                             f=tile_box.top,
                             a=(tile_box.right - tile_box.left) / 256.0,
                             e=(tile_box.bottom - tile_box.top) / 256.0)

            return src, dest




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
                left_top = max(left_top[0],0), max(left_top[1],0)
                right_bottom = invert_affine * (tile_box.right, tile_box.bottom)
                if round(left_top[0]) < raster.shape[1] and round(left_top[1]) < raster.shape[0]:

                    window = ((math.floor(left_top[1]), math.ceil(right_bottom[1])),
                              (math.floor(left_top[0]), math.ceil(right_bottom[0])))
                    array = raster.read(window=window)
                    src_affine, dest_affine = tile_affines(tile_box)
                    dest_array = np.zeros((raster.count, 256, 256), dtype=dtype)
                    if nodata:
                        dest_array.fill(nodata)
                    reproject(array,
                              dest_array,
                              src_transform=src_affine,
                              dst_transform=dest_affine)
                    # из полученых гео координат получаем размер результирующей картинки
                    dest_left, dest_top = ~dest_affine * src_affine * (0,0)
                    dest_right, dest_bottom = ~dest_affine * src_affine * array.shape[:0:-1]
                    dest_left, dest_top, dest_right, dest_bottom = map(round,(dest_left, dest_top, dest_right, dest_bottom))
                    # ресайзим вырезанный растр
                    # если оригинальная картинка на этом масштабе меньше чем 256х256
                    if dest_right - dest_left < 256 or dest_bottom - dest_top < 256:
                        if nodata is None:
                            mask = np.ma.getmaskarray(dest_array)
                            mask[:,dest_bottom:] = True
                            mask[:,:,dest_right:] = True
                            mask[:,:dest_top] = True
                            mask[:,:,:dest_left] = True
                            dest_array = np.ma.masked_array(dest_array,mask=mask)

                    if not np.ma.is_masked(dest_array) and nodata:
                        dest_array = np.ma.masked_values(dest_array, nodata, copy=False)

                    if raster.count == 1: # grid with one channel

                        rgba = ScalarMappable(cmap='gist_earth', norm=SymLogNorm(1, vmin=vmin, vmax=vmax, clip=True)).to_rgba(dest_array[0], alpha=0.7)
                        rgba *= 255
                        rgba = np.asarray(rgba, dtype='uint8')
                    elif raster.count == 3: # image with RGB so add A
                        rgba = np.empty((dest_array.shape[1], dest_array.shape[2],4), dtype='uint8')
                        rgba.fill(255 )
                        rgba[:,:,:-1] = reshape_as_image(dest_array)
                        if np.ma.is_masked(dest_array):
                            rgba[..., 3] = (~dest_array.mask[0]).astype('uint8') * (255 )
                            pass


            output = BytesIO()
            Image.fromarray(rgba, mode='RGBA').save(output, 'PNG')
            output.seek(0)
            response = flask.send_file(output, mimetype='image/png')
            response.headers['Cache-Control'] = 'no-cache'
            return response



        server = wsgi.WSGIServer((host, port), application=app, log=None)
        server.serve_forever()


###############################################################################
#  Main
###############################################################################
if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5000
    raster = None
    try:
        if len(sys.argv) > 1:
            path = sys.argv[1]
        else:
            assert len(glob.glob('*.tif')), "no GeoTiff files in current directory"
            path = glob.glob('*.tif')[0]
        assert os.path.exists(path), "file not exists {}".format(path)
        # path = 'marinka_img.tif'
        raster_path = reproject_tif(path)

        vmin, vmax = 0, 0
        lnglat = (0,0)
        with rasterio.open(raster_path, 'r') as raster:
            d = raster.read()
            vmin, vmax = d.min(), d.max()
            lnglat = raster.lnglat()
            zoom = math.ceil( math.log(20037508.3427892*2 / (raster.res[1] * raster.width), 2) )
            del d
            webservers = []
        webservers.append( multiprocessing.Process(
            target=run_index_webserver,
            args=(raster_path, lnglat, zoom, host, port)
        ))

        for i in range(1,4):
            webservers.append(multiprocessing.Process(
                target=run_title_webserver,
                args=(raster_path, vmin, vmax, host, port + i)
            ))

        for ws in webservers:
            ws.start()

        for ws in webservers:
            ws.join()


    except KeyboardInterrupt:
        raster.close()
    except Exception as ex:
        print("{}: {}".format(type(ex).__name__, str(ex)))
