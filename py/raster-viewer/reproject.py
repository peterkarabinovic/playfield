# coding: utf-8
import glob
import os
import sys
import rasterio
import osr
import numpy as np
from rasterio.coords import BoundingBox
from rasterio.warp import reproject, RESAMPLING

import warnings
warnings.filterwarnings("ignore")

def reproject_tif(path):

    with rasterio.Env():

        with rasterio.open(path,'r') as src:

            src_crs = osr.SpatialReference()
            src_crs.ImportFromWkt(src.crs.wkt)
            wgs_crs = osr.SpatialReference()
            wgs_crs.ImportFromEPSG(4326)
            tms_crs = osr.SpatialReference()
            tms_crs.ImportFromEPSG(3857)



            # переводим bounds of src в wgs84 обрезаем по tms bounds и обратно в проекцкию источника
            crsSrc_to_wgs = osr.CoordinateTransformation(src_crs, wgs_crs).TransformPoints
            crsWgs_to_src = osr.CoordinateTransformation(wgs_crs, src_crs).TransformPoints
            tms_bounds = BoundingBox(-179.99999999999955,-85.05112877980004, 179.99999999999955, 85.05112877979995)
            lb, rt = crsSrc_to_wgs([(src.bounds.left,src.bounds.bottom), (src.bounds.right, src.bounds.top)])
            clip_bounds = BoundingBox(lb[0], max(lb[1], tms_bounds.bottom), rt[0], min(rt[1], tms_bounds.top))
            clip_lb, clip_rt = crsWgs_to_src([(clip_bounds.left,clip_bounds.bottom),(clip_bounds.right,clip_bounds.top)])
            src_clip_transform = list(src.transform)
            src_clip_transform[3] = clip_rt[1]

            # теперь высчитываем окно которое нужно вырезать из исходных данных
            inv = ~src.affine
            row_start = int(round( (~src.affine * clip_rt[:2])[1] ))
            row_stop = int(round( (~src.affine * clip_lb[:2])[1] ))
            window = ( (row_start, row_stop), (0,src.width) )

            # подсчитываем геотраснформ для результата
            crsWgs_to_tms = osr.CoordinateTransformation(wgs_crs, tms_crs).TransformPoints
            dst_lb, dst_rt = crsWgs_to_tms([(clip_bounds.left, clip_bounds.bottom), (clip_bounds.right, clip_bounds.top)])
            dst_width, dst_height = src.width, int(row_stop - row_start)
            dst_transform = [dst_lb[0], (dst_rt[0] - dst_lb[0]) / dst_width, 0, dst_rt[1], 0, (dst_rt[1] - dst_lb[1]) / dst_height ]
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

            name, ext = os.path.splitext(path)
            dst_path = name + "_3857" + ext

            with rasterio.open(dst_path, 'w',
                               driver='GTiff',
                               width=dst_width,
                               height=dst_height,
                               count=src.count,
                               dtype=dst.dtype,
                               crs = 'EPSG:3857',
                               transform=dst_transform,
                               nodata=src.profile['nodata']) as f:
                f.write(dst)







if __name__ == '__main__':

    raster = None
    try:
        if len(sys.argv) > 1:
            path = sys.argv[1]
        else:
            assert len(glob.glob('*.tif')), "no GeoTiff files in current directory"
            path = glob.glob('*.tif')[0]
        assert os.path.exists(path), "file not exists {}".format(path)

        raster = reproject_tif(path)

    except KeyboardInterrupt:
        raster.close()
    except Exception as ex:
        print("Error: {}".format(str(ex)))
