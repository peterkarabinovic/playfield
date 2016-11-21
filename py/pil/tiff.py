# coding: utf-8
import numpy as np
from PIL import Image

im = Image.open('a_image.tif')
im.show()

x = np.array(im)
print x
