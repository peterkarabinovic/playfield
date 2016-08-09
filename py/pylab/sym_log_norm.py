import numpy as np
import matplotlib.colors
import pylab



x = np.linspace(-1000,1000, 100)

norm = matplotlib.colors.Normalize()
norm.autoscale(x)
norm_y = norm(x)
pylab.plot(x,norm_y,label='Normalize')


lognorm = matplotlib.colors.LogNorm()
lognorm.autoscale(x)
lognorm_y =  lognorm(x) 
pylab.plot(x,lognorm_y,label='LogNorm')


symlognorm = matplotlib.colors.SymLogNorm(linthresh=5)
symlognorm.autoscale(x)
symlognorm_y = symlognorm(x)
pylab.plot(x,symlognorm_y,label='SymLogNorm')


powernorm = matplotlib.colors.PowerNorm(gamma=1./2.)
powernorm.autoscale(x)
powernorm_y = powernorm(x)
pylab.plot(x,powernorm_y,label='PowerNorm')

nonorm = matplotlib.colors.NoNorm()
nonorm.autoscale(x)
nonorm_y = nonorm(x)
pylab.plot(x,nonorm_y,label='NoNorm')

pylab.legend(loc='upper left', frameon=False)
pylab.show()

