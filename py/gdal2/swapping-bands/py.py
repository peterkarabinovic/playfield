import gdalnumeric

# name of our source image
src = "FalseColor.tif"

# load the source image into an array
arr = gdalnumeric.LoadFile(src)

print arr.flat
# swap bands 1 and 2 for a natural color image.
# We will use numpy "advanced slicing" to reorder the bands.
# Using the source image
# gdalnumeric.SaveArray(arr[[1,0,2],:], "swap.tif", format="GTiff", prototype=src)

