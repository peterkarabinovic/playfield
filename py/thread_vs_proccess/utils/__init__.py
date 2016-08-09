#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time

import re


def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        try:
            print('%s function took %0.3f ms' % (f.__name__, (time2-time1)*1000.0))
        except Exception:
            pass

        return ret
    return wrap

# Размер файла в читабельной форме
def filesize(bytes):
    alternative = [
        (1024 ** 5, ' PB'),
        (1024 ** 4, ' TB'),
        (1024 ** 3, ' GB'),
        (1024 ** 2, ' MB'),
        (1024 ** 1, ' KB'),
        (1024 ** 0, (' byte', ' bytes'))]
    for factor, suffix in alternative:
        if bytes >= factor:
            break
    amount = int(bytes/factor)
    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple
    return str(amount) + suffix

def filename(filepath):
    return re.sub(r'^\d+_(\D+)$', r'\1', os.path.splitext(os.path.basename(filepath.lower()))[0])


def listTree(path, excludeDirs=[], excludeFilenames=[]):
    if not os.path.exists(path):
        return
    path = os.path.abspath(path)
    for dirpath, dirs, files in os.walk(path, topdown=True):
        dirs[:] = [d for d in dirs if d not in excludeDirs]
        for f in sorted(files):
            if filename(f) in excludeFilenames:
                continue
            yield os.path.join(dirpath, f)
