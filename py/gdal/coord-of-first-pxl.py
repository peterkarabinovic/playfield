# coding: utf-8
import gdal
import affine
import osr
# gtif = gdal.Open('D:/documents/shared/vgrids/srid3785/NH/n44_e022_1arc_v3.tif')
gtif = gdal.Open('n100x100.tif')
gtif.GetGeoTransform()
fwd = affine.Affine.from_gdal(*gtif.GetGeoTransform())
first_pxl = fwd * (0,0)   # 2449013.3364116307, 5621543.351431573 
sp4326 = osr.SpatialReference()
sp4326.ImportFromEPSG(4326)
sp3857 = osr.SpatialReference(  gtif.GetProjectionRef() )
transform = osr.CoordinateTransformation(sp3857, sp4326)
print transform.TransformPoint( *first_pxl )

