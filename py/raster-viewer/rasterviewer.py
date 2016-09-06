# coding: utf-8

"""
    Скрипт позволяет простматривать растровые файлы в браузере,
    запуская wsgi http server и реализуя компактный TMS сервис.
    Файл перепроецируется в EPSG:3857, затем запускается Flask Web Service
    который обрабатывае z/y/x запорсы, возвращая вырезанный и смаштабированный тайл
"""

from __future__ import print_function

###############################################################################
#  Проверяем есть ли все необходимы модули
###############################################################################
import imp, sys

def check_module(name):
    try:
        imp.find_module(name)
    except ImportError:
        print("Error: '{}' module not installed.\nTry in Anaconda:\n\t$ conda install {}".format(name,name) )
        sys.exit(1)

check_module('numpy')
check_module('osr')
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
import osr
import numpy as np

###############################################################################
#  Перепроецирование растра если не EPSG:3857
###############################################################################
from rasterio.coords import BoundingBox
from rasterio.warp import reproject, RESAMPLING
import warnings
warnings.filterwarnings("ignore")

def reproject_tif(path):

    with rasterio.Env():
        with rasterio.open(path, 'r') as src:

            if src.crs == {'init': 'epsg:3857'}:
                return path

            name, _ = os.path.splitext(path)
            dst_path = name + "_3857.tif"

            if os.path.exists(dst_path):
                return dst_path

            src_crs = osr.SpatialReference()
            src_crs.ImportFromWkt(src.crs.wkt)
            wgs_crs = osr.SpatialReference()
            wgs_crs.ImportFromEPSG(4326)
            tms_crs = osr.SpatialReference()
            tms_crs.ImportFromEPSG(3857)

            # переводим bounds of src в wgs84 обрезаем по tms bounds и обратно в проекцкию источника
            crsSrc_to_wgs = osr.CoordinateTransformation(src_crs, wgs_crs).TransformPoints
            crsWgs_to_src = osr.CoordinateTransformation(wgs_crs, src_crs).TransformPoints
            tms_bounds = BoundingBox(-179.99999999999955, -85.05112877980004, 179.99999999999955, 85.05112877979995)
            lb, rt = crsSrc_to_wgs([(src.bounds.left, src.bounds.bottom), (src.bounds.right, src.bounds.top)])
            clip_bounds = BoundingBox(lb[0], max(lb[1], tms_bounds.bottom), rt[0], min(rt[1], tms_bounds.top))
            clip_lb, clip_rt = crsWgs_to_src([(clip_bounds.left, clip_bounds.bottom), (clip_bounds.right, clip_bounds.top)])
            src_clip_transform = list(src.transform)
            src_clip_transform[3] = clip_rt[1]

            # теперь высчитываем окно которое нужно вырезать из исходных данных
            inv = ~src.affine
            row_start = int(round((~src.affine * clip_rt[:2])[1]))
            row_stop = int(round((~src.affine * clip_lb[:2])[1]))
            window = ((row_start, row_stop), (0, src.width))

            # подсчитываем геотраснформ для результата
            crsWgs_to_tms = osr.CoordinateTransformation(wgs_crs, tms_crs).TransformPoints
            dst_lb, dst_rt = crsWgs_to_tms([(clip_bounds.left, clip_bounds.bottom), (clip_bounds.right, clip_bounds.top)])
            dst_width, dst_height = src.width, int(row_stop - row_start)
            dst_transform = [dst_lb[0], (dst_rt[0] - dst_lb[0]) / dst_width, 0, dst_rt[1], 0,(dst_rt[1] - dst_lb[1]) / dst_height]
            if dst_transform[5] > 0:
                dst_transform[5] = -dst_transform[5]

            dst = np.zeros((src.count, dst_height, dst_width), src.profile['dtype'])

            reproject(
                src.read(window=window),
                dst,
                src_transform=src_clip_transform,
                dst_transform=dst_transform,
                src_crs=src.crs,
                dst_crs='EPSG:3857',
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
        zoom: 7,
        layers : [
            new L.TileLayer('http://tms{s}.visicom.ua/2.0.0/planet3/base_ru/{z}/{x}/{y}.png',{
                    maxZoom : 19,
                    tms : true,
                    attribution : 'Данные компании © <a href="http://visicom.ua/">Визиком</a>',
                    subdomains : '123'
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
        min, max = d.min(), d.max()
        del d

        app = flask.Flask(__name__)

        @app.route('/<int:z>/<int:x>/<int:y>')
        def tile(z,x,y):
            step = ( tms_box.right - tms_box.left ) / ( 2 ** z)
            tile_box = BoundingBox(tms_box.left + x * step,
                                    tms_box.bottom + y *step,
                                    tms_box.left + (x + 1)* step,
                                   tms_box.bottom + (y + 1)  * step)
            if not disjoint_bounds(raster.bounds,tile_box):
                lt = invert_affine * (tile_box.left, tile_box.top)
                rb = invert_affine * (tile_box.right, tile_box.bottom)
                window = ( (lt[1],rb[1]), (lt[0],rb[0]) )
                array = raster.read(window=window)

                if raster.count == 1: # grid with on channel
                    rgba = ScalarMappable(cmap='autumn', norm=SymLogNorm(1, vmin=array.min(), vmax=array.max(), clip=True)).to_rgba(array[0], alpha=0.7)
                    rgba *= 255
                    rgba = np.asarray(rgba, dtype='uint8')
                elif raster.count == 3: # image with RGB so add A
                    zeros = np.zeros((1, raster.height, raster.width), dtype=int)
                    rgba = np.append( array, zeros, axis=0)
            else:
                rgba = empty_tile

            output = BytesIO()
            Image.fromarray(rgba, mode='RGBA').save("7_79_94.png", 'PNG')
            Image.fromarray(rgba, mode='RGBA').save(output, 'PNG')
            output.seek(0)
            return flask.send_file(output, mimetype='image/png')


        @app.route('/')
        def index():
            global index_html
            index_html = index_html.replace('${raster_name}', os.path.basename(raster_path))
            index_html = index_html.replace('${latlng}', str(list(raster.lnglat())[::-1]))
            return index_html

        gevent.spawn(lambda: webbrowser.open(('http://%s:%s') % (host, port)))
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
        path = "bathymetry_3857.tif"
        assert os.path.exists(path), "file not exists {}".format(path)

        raster_path = reproject_tif(path)
        run_web(raster_path, port=5000)
    except KeyboardInterrupt:
        raster.close()
    except Exception as ex:
        print("Error: {}".format(str(ex)))
