import numpy as np
import pylab

#Load the dataset
data = np.loadtxt('ex1data1.txt', delimiter=',')
#Plot the data
pylab.scatter(data[:, 0], data[:, 1], marker='o', c='b')
pylab.title('Profits distribution')
pylab.xlabel('Population of City in 10,000s')
pylab.ylabel('Profit in $10,000s')
pylab.show()
