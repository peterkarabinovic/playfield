import gdalnumeric

def histogram(a, bins=range(0,256)):
    """
    Histogram function for multi-dimensional array.
    a = array
    bins = range of numbers to match
    """
    fa = a.flat
    n = gdalnumeric.numpy.searchsorted(gdalnumeric.numpy.sort(fa),
    bins)
    n = gdalnumeric.numpy.concatenate([n, [len(fa)]])
    hist = n[1:]-n[:-1]
    return hist

arr = gdalnumeric.LoadFile("swap.tif")
histograms = []
for b in arr:
    histograms.append(histogram(b))

help(gdalnumeric.numpy.concatenate)