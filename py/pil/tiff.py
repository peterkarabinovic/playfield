# coding: utf-8
from PIL import Image
import numpy as np
im = Image.open('a_image.tif')
im.show()

a = np.array(im)
