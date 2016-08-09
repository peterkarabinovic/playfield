import numpy as np
check = np.zeros((9, 9))
check[::2, 1::2] = 1
check[1::2, ::2] = 1
import mayavi.mlab  as mlab


x, y, z, value = np.random.random((4, 40))
mlab.points3d(x, y, z, value)