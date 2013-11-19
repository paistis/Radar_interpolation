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
import matplotlib.pyplot as plt


def get_sweep(radar,field,sweep):
	starts = radar.sweep_start_ray_index['data']
        ends = radar.sweep_end_ray_index['data']
        start = starts[sweep]
        end = ends[sweep] + 1
        data = radar.fields[field]['data'][start:end]
	radar.fields[field]['data'] = data
	print data.shape
	radar.azimuth['data'] = radar.azimuth['data'][start:end]
	radar.elevation['data'] = radar.elevation['data'][start:end]
	#radar.range['data'] = radar.range['data'][start:end]

#definitions for mask from HCLASS
rain=2
wet_snow=3
snow=4
graupel=5
hail=6
def interpolate(RADAR_FILE1_path,RADAR_FILE2_path,timesteps,images,morph,filename,interpolated_variables = ['DBZ2','HCLASS2']):
	# Variables
	RADAR="VAN"
	#RADAR_FILE1_path = "/home/nordlikg/Documents/data/RAW/VAN/2010-07-15/201007151155_VAN.PPI3_B.raw" #'201008081800_VAN.PPI1_A.raw'
	#RADAR_FILE2_path = "/home/nordlikg/Documents/data/RAW/VAN/2010-07-15/201007151215_VAN.PPI1_B.raw"#'201008081820_VAN.PPI2_A.raw'
	RADAR_FILE1 = os.path.basename(RADAR_FILE1_path)
	RADAR_FILE2 = os.path.basename(RADAR_FILE2_path)
	movement_variable = 'DBZ2'
	interpolated_variables = ['DBZ2','HCLASS2']
	mask=rain
	#timesteps = 10
	#images = "images2/"
	#morph = "morp2/"
	#filename="test"
	path = os.getcwd()
	sweep=0
	treshold=0.3

	#Read radar data
	print "Reading radar files"
	radar1 = pyart.io.read_sigmet(RADAR_FILE1_path,sigmet_field_names=True, time_ordered='none')
	radar2 = pyart.io.read_sigmet(RADAR_FILE2_path,sigmet_field_names=True, time_ordered='none')
	print radar1.fields.keys()
	# mask out last 10 gates of each ray, this removed the "ring" around th radar.
	#radar1.fields['DBZ2']['data'][:, -10:] = np.ma.masked
	#radar2.fields['DBZ2']['data'][:, -10:] = np.ma.masked

	#get sweep

	print "geting sweep"
	for field, field_dic in radar1.fields.iteritems():
		get_sweep(radar1,field,sweep)
		get_sweep(radar2,field,sweep)

	#saving non masked data
	display = pyart.graph.RadarDisplay(radar1)
	for field, field_dic in radar1.fields.iteritems():
		geotiff2png.radarDisplay2geotiff(radar1,display,field+".tiff",field,0)

	#data quality control
	print "masking radar data"

	#mask for first grid
	mask_ =  radar1.fields['HCLASS2']['data']
	mask_[mask_.mask] = nan
	mask_ = mask_.data
	mask_[(mask+treshold) < mask_] = nan
	mask_[(mask-treshold) > mask_] = nan
	mask_[np.isfinite(mask_)] = 1

	#mask for second grid
	mask_2 =  radar2.fields['HCLASS2']['data']
	mask_2[mask_2.mask] = nan
	mask_2 = mask_2.data
	mask_2[(mask+treshold) < mask_2] = nan
	mask_2[(mask-treshold) > mask_2] = nan
	mask_2[np.isfinite(mask_2)] = 1

	for field in interpolated_variables:
		if (field != "ROI"):# and (field != "HCLASS2"):		
			radar1.fields[field]['data'] = np.ma.MaskedArray(radar1.fields[field]['data'].data*mask_,radar1.fields[field]['data'].mask)
			radar2.fields[field]['data'] = np.ma.MaskedArray(radar2.fields[field]['data'].data*mask_2,radar2.fields[field]['data'].mask)

	# perform Cartesian mapping, limit to the reflectivity field.
	#grid1 = pyart.io.grid.read_grid("test_grid1.nfc")
	#grid2 = pyart.io.grid.read_grid("test_grid2.nfc")

	print "griding first file..."
	dist = radar1.range['data'][-1]
	rcells = radar1.ngates

	grid1 = pyart.map.grid_from_radars(
	    (radar1,),
	    grid_shape=(rcells, rcells, 3),
	    grid_limits=((dist, -dist), (dist, -dist),
		         (10, 10)),
	    fields=interpolated_variables,leafsize = 50)
	print "saving grid one"
	grid1.write(filename+"_grid1.nfc")

	print "griding second file..."
	grid2 = pyart.map.grid_from_radars(
	    (radar2,),
	    grid_shape=(rcells, rcells, 3),
	    grid_limits=((dist, -dist), (dist, -dist),
		         (10, 10)),
	    fields=interpolated_variables,leafsize = 50)
	print "saving second grid.."
	grid2.write(filename+"_grid2.nfc")

	#data Quality control

	grid1.write(images+RADAR_FILE1+"nonmasked.tiff",'GTiff')
	grid2.write(images+RADAR_FILE2+"nonnmasked.tiff",'GTiff')


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
		ifiles = glob.glob('*'+i+'*.png')
		for ifile in ifiles:
			ofile, ext = os.path.splitext(ifile)
			ofile = path+"/"+morph+ofile + ".tiff"
			geotiff2png.png2geotiff(ifile,i,ofile,grid1)
			os.remove(ifile)

