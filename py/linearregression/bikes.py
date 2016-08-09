import pandas as pd
import pylab

bikes = pd.read_csv('bikes.csv')
print bikes.head()

pylab.figure(figsize=(8,6))
pylab.plot(bikes['temperature'], bikes['count'], 'o')
pylab.xlabel('temperature')
pylab.ylabel('bikes')
pylab.show()