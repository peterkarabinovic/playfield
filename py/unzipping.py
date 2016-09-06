"""
    Unpack data files in particular folders
"""
import zipfile
import os
import glob
from multiprocessing.pool import Pool, ThreadPool
import time
import shutil
import rasterio as rio



# 1. extract raster data from zip-file
def unzip(filepath):
    datadir = os.path.basename(filepath).replace('_grid.zip','/')
    if os.path.exists(datadir):
        return
    print 'unzip', filepath
    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            members = [f for f in zf.namelist() if f.startswith(datadir)]
            zf.extractall(members=members)
    except Exception as ex:
        print (filepath + '  ' + str(ex))
    return datadir.replace('/','')


# 2. convert ESRI GRID data into GTiff
def convert_tiff(adf_dir):
    if not os.path.exists(adf_dir):
        return adf_dir
    print 'convert_tiff', adf_dir
    esrigrid = os.path.join(adf_dir,adf_dir,'w001001.adf')
    tiffname = adf_dir + '.tiff'
    with rio.open(esrigrid) as src:
        data = src.read(1)
        if 'uint8' in src.dtypes:
            data = data.astype('int16', casting='unsafe', copy=False)
            data[data == 255] = -32768
        profile = src.profile
        with rio.open(tiffname, 'w',
                      driver='GTiff',
                      width=src.width,
                      height=src.height,
                      count=1,
                      dtype='int16',
                      crs=profile['crs'],
                      transform=profile['affine'],
                      nodata=-32768) as dst:
            dst.write(data, 1)
    return adf_dir


# 3. delete extracted data
def remove(adf_dir):
    if not os.path.exists(adf_dir):
        return
    print 'remove', adf_dir
    shutil.rmtree(adf_dir)

# this function becouse multiprocessing.pool
def process(f):
    remove(convert_tiff(unzip(f)))


if __name__ == '__main__':
    start_time = time.time()
    # read only those zip files that not converted yet
    files = [ f for f in glob.glob('*.zip')  if not os.path.exists(f.replace('_grid.zip', '.tiff')) ]
    pool = Pool(10)
    pool.map(process, files)
    print("--- %s seconds ---" % (time.time() - start_time))

