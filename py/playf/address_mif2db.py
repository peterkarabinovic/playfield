# coding=utf-8
import os
import subprocess
from multiprocessing.pool import ThreadPool

# Ищем рекурсивно и загрузаем global.properties
properties = {}
dir, tail = os.path.split(__file__)
while tail:
    gp = os.path.join(dir,'global.properties')
    if os.path.exists(gp):
        for line in open(gp):
            line = line.strip()
            if line.count('#') or line.count('=') == 0: continue;
            name, value = line.split('=');
            properties[name.strip()] = value.strip();
        break
    dir, tail = os.path.split(dir)

# Читаем properties
url = properties['poi.db.url']
user = properties['poi.db.login']
pswd = properties['poi.db.password']
dbname = url[url.rfind('/')+1:]
host = url[url.find('//')+2:url.rfind(':')]

pool = None
# Бежим по всем папкам и ищем adr.mif/bd.mif/str_l.mif
def eachDirectory(arg, dirname, names):
    global pool
    if dirname.count('Ukraine_3.2'): return
    adr_mif = dirname  + '\\adr.mif'
    bd_mif = dirname  + '\\bd.mif'
    str_mif = dirname  + '\\Graf_auto.mif'
    if os.path.exists(adr_mif) and os.path.exists(bd_mif) and os.path.exists(str_mif):
        def mif2db(mif):
            print '\t%s' % mif
            cmd = 'ogr2ogr -append -skipfailures -a_srs EPSG:4326 -f PostgreSQL '\
                  'PG:"dbname=' + dbname + ' user=' + user + ' password=' + pswd + ' host=' + host + '" ' + \
                   mif + ' -lco SCHEMA=temp -nln temp.' + os.path.basename(mif)[0:-4]
            os.environ['PGCLIENTENCODING'] = 'windows-1251'
            subprocess.check_call(cmd)

        if pool == None: # первый раз запускаем не асинхронно (что бы создались таблицы)
            mif2db(str_mif);
            mif2db(adr_mif);
            mif2db(bd_mif);
            pool = ThreadPool(7);
        else:
            pool.apply_async(mif2db, [str_mif]);
            pool.apply_async(mif2db, [adr_mif]);
            pool.apply_async(mif2db, [bd_mif]);

os.path.walk('//Lena-bases/D/WORLD/UKRAINE/',eachDirectory,None)
pool.close()
pool.join()






