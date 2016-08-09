from osgeo import gdal
xml = """<GDAL_WMS>
<Service name="TMS">
<ServerUrl>http://tms.visicom.ua/2.0.0/planet3/base/${z}/${x}/${y}.png</ServerUrl>
</Service>
<DataWindow>
<UpperLeftX>-20037508.2</UpperLeftX>
<UpperLeftY>20037508.3</UpperLeftY>
<LowerRightX>20037508.2</LowerRightX>
<LowerRightY>-20037508.3</LowerRightY>
<TileLevel>19</TileLevel>
<TileCountX>1</TileCountX>
<TileCountY>1</TileCountY>
<YOrigin>bottom</YOrigin>
</DataWindow>
<Projection>EPSG:3857</Projection>
<BlockSizeX>256</BlockSizeX>
<BlockSizeY>256</BlockSizeY>
<BandsCount>3</BandsCount>
<Cache />
</GDAL_WMS>"""
vfn = "/vsimem/visicom.xml"
gdal.FileFromMemBuffer(vfn, xml)
rasterLyr = QgsRasterLayer(vfn, "Visicom")
QgsMapLayerRegistry.instance().addMapLayers([rasterLyr])