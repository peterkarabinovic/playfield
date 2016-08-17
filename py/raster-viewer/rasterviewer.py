# coding: utf-8

"""
    Скрипт позволяет простматривать растровые файлы в браузере,
    реализуя компактный TMS сервис.
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

check_module('osr')
check_module('rasterio')
check_module('PIL')
check_module('flask')


import os
import sys
import glob
import rasterio
import osr
###############################################################################
#  Перепроецирование растра если не EPSG:3857
###############################################################################
def raster_in_3857(path):
    with rasterio.open(path, 'r') as src:
        affine = src.profile['affine']
        bounds = src.bounds

    #  C rasterio функция calculate_default_transform выдает MemoryError для больших файлов
    # with rasterio.open(path,'r') as src:
    #     if src.crs != 'EPSG:3857':
    #         name, ext = os.path.splitext(path)
    #         path3857 = name + "-3857" + ext
    #         if os.path.exists(path3857):
    #             with rasterio.open(path3857,'r') as raster3857:
    #                 if raster3857.crs == 'EPSG:3857':
    #                     return rasterio.open(path3857,'r')
    #         profile = src.profile
    #         affine, width, height = rasterio.warp.calculate_default_transform(
    #             src.crs, 'EPSG:3857', src.width, src.height, *src.bounds)
    #         with rasterio.open(path3857,'w',
    #                            driver='GTiff',
    #                            width=width,
    #                            height=height,
    #                            count=src.count,
    #                            dtype=profile['dtype'],
    #                            crs = 'EPSG:3857',
    #                            transform=affine,
    #                            nodata=profile['nodata'],
    #                            ) as dst:
    #             dst.write(src.read())
    #             return rasterio.open(path3857,'r')
    #     else:
    #         return rasterio.open(path,'r')




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

        raster = raster_in_3857(path)

    except KeyboardInterrupt:
        raster.close()
    except Exception as ex:
        print("Error: {}".format(str(ex)))
