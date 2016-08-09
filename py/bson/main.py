#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict

import struct

from six import StringIO, BytesIO
import socket

import bson, time
import timeit

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

import ctypes
header = ctypes.create_string_buffer(8)

def sendobj(buf):
    global s
    size = len(buf)
    struct.pack_into('<ii',header, 0, 1000, size)
    s.sendall(header)
    s.sendall(buf)

def receive(bytes_needed, sock_buf = None):
    if sock_buf is None:
        sock_buf = BytesIO()
    bytes_recd = 0
    while bytes_recd < bytes_needed:
        chunk = s.recv(min((bytes_needed - bytes_recd), 2048))
        part_count = len(chunk)
        if part_count < 1:
            return None
        bytes_recd += part_count
        sock_buf.write(chunk)
    return sock_buf

def receiveobj():
    h = receive(8)
    h = struct.unpack('<ii',h.getvalue())
    size = h[1]
    return receive(size)


query = OrderedDict([ ("database", "dapi"),
                      ("mapview", "base"),
                      ("lang", "ru"),
                      ("method", "search"),
                      ("categories", "adr_street"),
                      ("limit", 256),
                      ("text", "СВОБО"),
                      ("country", "ua"),
                      ("intersect", "STL1NT7FL")])



time.clock();
for i in xrange(1000*1000):
    bson.dumps(query)
print("Time " + str(time.clock()))

# s.connect(("127.0.0.1", 1000))
# buf = bson.dumps(query)
# sendobj(buf)
# buf = receiveobj()
# d = bson.loads(buf.getvalue())
# #
# print(d)