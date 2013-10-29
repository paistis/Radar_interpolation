import sys, os, time
from scipy import ndimage
from scipy import misc
import scipy.io
from matplotlib.image import AxesImage
from pylab import *
import gdal,cmath
import numpy as np
import pyart
import geotiff2png
import subprocess
import glob

# Variables
RADAR_FILE1 = '201008081800_VAN.PPI1_A.raw'
RADAR_FILE2 = '201008081805_VAN.PPI2_A.raw'
movement_variable = 'reflectivity_horizontal'
interpolated_variables = ['reflectivity_horizontal']
timesteps = 10
images = "images/"
morph = "morp/"
filename="test"
path = os.getcwd()

#Read radar data 
radar1 = pyart.io.read_rsl(RADAR_FILE1)
radar2 = pyart.io.read_rsl(RADAR_FILE2)

print "Reading radar files"

dist = radar1.range['data'][-1]
rcells = radar1.ngates
# mask out last 10 gates of each ray, this removed the "ring" around th radar.
radar1.fields['reflectivity_horizontal']['data'][:, -10:] = np.ma.masked
radar2.fields['reflectivity_horizontal']['data'][:, -10:] = np.ma.masked


# perform Cartesian mapping, limit to the reflectivity field.
#grid1 = pyart.io.grid.read_grid("test_grid1.nfc")
#grid2 = pyart.io.grid.read_grid("test_grid2.nfc")
print "griding first file..."
grid1 = pyart.map.grid_from_radars(
    (radar1,),
    grid_shape=(rcells*2, rcells*2, 5),
    grid_limits=((dist, -dist), (dist, -dist),
                 (10, 10)),
    fields=interpolated_variables)
print "saving grid one"
grid1.write(filename+"_grid1.nfc")

print "griding second file..."
grid2 = pyart.map.grid_from_radars(
    (radar2,),
    grid_shape=(rcells*2, rcells*2, 5),
    grid_limits=((dist, -dist), (dist, -dist),
                 (10, 10)),
    fields=interpolated_variables)
print "saving second grid.."
grid1.write(filename+"_grid2.nfc")

grid1.write(images+RADAR_FILE1+".tiff",'GTiff')
grid2.write(images+RADAR_FILE2+".tiff",'GTiff')


#at this point we have start and end images for the interpolation
#step 1. make grayscale images: 8-bit for calculating motion field, 16-bit for interpolation (output formats are png) and size is next power of 2
print "converting pictures..."
image1 = images+RADAR_FILE1  +"_"+movement_variable+".tiff"
image2 = images+RADAR_FILE2 +"_"+movement_variable+".tiff"
image1_png = images+RADAR_FILE1 +"_"+movement_variable+"_8bit"+".png"
image2_png = images+RADAR_FILE2 +"_"+movement_variable+"_8bit"+".png"

geotiff2png.geotiff2png(image1,movement_variable,image1_png,True)
geotiff2png.geotiff2png(image2,movement_variable,image2_png,True)

#convert interpolated values to 16bit png's

for i in interpolated_variables:
	geotiff2png.geotiff2png(images+RADAR_FILE1 +"_"+ i+".tiff",i,images+RADAR_FILE1 +i+".png",False)
	geotiff2png.geotiff2png(images+RADAR_FILE2 +"_"+ i+".tiff",i,images+RADAR_FILE2 +i+".png",False)



#step 2. calculate motion vectors from movement_variable
print "calculating motion..."
args = path+"/optflow_8bit/build/bin/morph --image1 "+image1_png+" --image2 "+image2_png+" --numtimesteps "+str(timesteps)+" --algorithm proesmans --outprefix "+filename+"_motion"
os.system(args)

#step 2. interploate all interpolation variables using 16-bit optical flow algorithm
print "interploating"
path = os.getcwd()
for i in interpolated_variables:
	print "interpolating" + str(i) 
	image1 = images+RADAR_FILE1 +i+".png"
	image2 = images+RADAR_FILE2 +i+".png"
	vec1 = filename+"_motion-motion1.pdvm"
	vec2 = filename+"_motion-motion2.pdvm"

	args=path+"/optflow/build/bin/morph3 --image1 " +image1+" --image2 "+image2+" --numtimesteps "+str(timesteps)+ " --algorithm proesmans --outprefix " + filename+"_"+i + " --vec1 "+vec1+" --vec2 "+ vec2
	os.system(args)

print "making geotiffs"
#step 3 make geotiff's from interpolated images
for i in interpolated_variables:
	ifiles = glob.glob('*reflectivity_horizonta*.png')
	for ifile in ifiles:
		ofile, ext = os.path.splitext(ifile)
		ofile = path+"/"+morph+ofile + ".tiff"
		geotiff2png.png2geotiff(ifile,i,ofile,grid1)
		os.remove(ifile)



		




