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
import shutil
from PIL import Image, ImageDraw, ImageChops, ImageFilter
import matplotlib.pyplot as plt
import datetime

#Filter definitions for data quality and functions
#Use the filler filter
def median_filter(Data):
        """Use median filtering to create or modify a filtering mask.
    
    Input:
    Data -- data array or a boolean filtering mask
    
    Return a boolean filtering array, where True = meteorological value, 
    False = non-meteorological value.
    """
    # Check for type
        if Data.dtype != 'bool':
                hcmask = Data > 1
        else:
                hcmask = Data

        hcmaski = Image.fromarray(hcmask.astype('uint8'))
        hcmaski = hcmaski.filter(ImageFilter.MedianFilter)
        hcmask = asarray(hcmaski).astype('bool') # Boolean array
        return hcmask

def closing_filter(Data, size=3):
        """Use grey closing to create or modify a filtering mask. 
        
        Input can be either unfiltered data or a filtering mask.
    Data -- data array or a boolean filtering mask
    Size -- Size of closing footprint (an integer). Closing footprint is
            size*size square.
        
        Output is a filtering mask (= a boolean array, where True means
        meteorological value)
    """
    # Check for type
        if Data.dtype != 'bool':
                hcmask = Data > 1
        else:
                hcmask = Data
        footprint = ones((size, size))
        hcmaski = ndimage.grey_closing(hcmask, footprint=footprint, mode='constant')
        return hcmaski # Boolean array

def filler_filter(Data, nonmet=1):
        """Create a filtering mask for dBZ field from hydroclass information
        field.
        
        Mask is created by removing non-meteorological objects and filling
        resulting holes. Hydroclass information field remains unmodified.
        
        Input:
        Data -- Hydroclass information field in numpy.ndarray
        nonmet -- value of non-meteorological objects. Function assumes that
                          this value is the smallest positive (non-zero) value of
                          the classification values.
        
        Return a boolean filtering mask, where values True corresponds to 
        meteorological object and False to non-meteorological object.
        """
	#Data = Data.data[0,:,:]
        im1 = zeros_like(Data)
        im1[Data==nonmet] = 2 # Non-meteorological objects
        im1[Data>nonmet] = 1 # Meteorological objects
#        savetxt('Hclass_nofilled.txt',im1) # speckle hydro_class

        # Make a mask for removing non-mets from inside mets
        im2 = zeros_like(im1)
        im2[im1==1] = 1 # Meteorological objects
        im2 = padder(im2) # Pad, fill and remove padding
        im2 = imfill(im2,1)
        im2 = rmpadder(im2)
# Filtering
        im3 = im1 - im2
        im1[im3==1] = 1 # Meteorological objects
        retim = im1 == 1 # Boolean array
        del im1, im2, im3
        return retim

def padder(arr):
        """Pad an array with zeros."""
        r,c = arr.shape
        dt  =  arr.dtype # To preserve array's dtype
        rows = zeros((r,1),dt)
        cols = zeros((1,c+2),dt)
        rowpad = hstack((rows,arr,rows))
        colpad = vstack((cols,rowpad,cols))
        return colpad

def rmpadder(padded):
        """Remove padding created by padder."""
        r,c = padded.shape
        r = r-1
        c = c-1
        padded = padded[1:r, 1:c] # Don't take the paddings into account anymore
        return padded

def imfill(arr, edge):
    """Fill holes in images.
    
    NOTE: dtype of input array will be temporarily converted uint8!
    This is because PIL's fromarray function works only with numpy
    arrays of data type 'uint8'. This may cause some data losses, so 
    proceed with caution!
    
    Input:
    arr -- a numpy.array to be floodfilled
    edge -- a value of edges
    """
    # using arr.astype to preserve array's dtype, as fromarray requires
    # array whose dtype is uint8
    img = Image.fromarray(arr.astype('uint8')) # read-only
    aimg = img.copy()
    ImageDraw.floodfill(aimg, (0,0), edge, edge)
    invimg = ImageChops.invert(aimg)
    invarr = asarray(invimg)
    arr[invarr==255] = edge
    return arr

def get_sweep(radar,field,sweep):
	starts = radar.sweep_start_ray_index['data']
        ends = radar.sweep_end_ray_index['data']
        start = starts[sweep]
        end = ends[sweep] + 1
        data = radar.fields[field]['data'][start:end]
	radar.fields[field]['data'] = data
	radar.azimuth['data'] = radar.azimuth['data'][start:end]
	radar.elevation['data'] = radar.elevation['data'][start:end]
	#radar.range['data'] = radar.range['data'][start:end]

def mask_grid(grid):
	print "masking grid data"
	data = grid.fields['HCLASS2']['data']
	mask = filler_filter(data[0,:,:])
	for field, field_dic in grid.fields.iteritems():
		if (field != "ROI"):# and (field != "HCLASS2"):		
			grid.fields[field]['data'] = np.ma.MaskedArray(grid.fields[field]['data'].data*mask,grid.fields[field]['data'].mask)
	return grid

def mask_radar(radar):
	print "masking radar data"
	data = radar.fields['HCLASS2']['data']
	mask = filler_filter(data.data)
	for field, field_dic in radar.fields.iteritems():
		if (field != "ROI"):# and (field != "HCLASS2"):		
			radar.fields[field]['data'] = np.ma.MaskedArray(radar.fields[field]['data'].data*mask,radar.fields[field]['data'].mask)
	return radar

#definitions for mask from HCLASS
rain=2
wet_snow=3
snow=4
graupel=5
hail=6

def interpolate(RADAR_FILE1_path,RADAR_FILE2_path,timesteps,filename,sweep,interpolated_variables = ['DBZ2','HCLASS2'],outfile_dir='/home/Radar/Int_Data/',log=None):
	# Variables
	RADAR_FILE1 = os.path.basename(RADAR_FILE1_path)
	RADAR_FILE2 = os.path.basename(RADAR_FILE2_path)
	movement_variable = 'DBZ2'
	mask=rain
	path = os.getcwd()
	treshold=0.3
	maskin='none'	

	#Read radar data
	print "Reading radar files"
	radar1 = pyart.io.read_sigmet(RADAR_FILE1_path,sigmet_field_names=True, time_ordered='none')
	radar2 = pyart.io.read_sigmet(RADAR_FILE2_path,sigmet_field_names=True, time_ordered='none')
	print "Fields in radar1 data"
	print radar1.fields.keys()
	print "Fields in radar2 data"
	print radar2.fields.keys()
	# mask out last 10 gates of each ray, this removed the "ring" around th radar.
	#radar1.fields['DBZ2']['data'][:, -10:] = np.ma.masked
	#radar2.fields['DBZ2']['data'][:, -10:] = np.ma.maskedi
        # Data from raw file filename at the end should be interpolation interval(starting-endpoint)          there must be a fancy way of redaing the date also!
        radar1_info=geotiff2png.radar_info(radar1)
        radar2_info=geotiff2png.radar_info(radar1) 
        site=radar1_info['site']
        time=str(radar1_info['time'])
        date=time[0:10]
        print site
        print date

       #Checking the output directories exists otherwise create them     
        if not os.path.exists(outfile_dir):
               os.makedirs(outfile_dir)
        date_path=outfile_dir+date
        if not os.path.exists(date_path):
                os.makedirs(date_path)
        site_path=date_path+'/'+site+'/'
        if not os.path.exists(site_path):
                os.makedirs(site_path) 
        if not os.path.exists(site_path+'/images/'):
               os.makedirs(site_path+'/images')
        images=site_path+'/images/'
        if not os.path.exists(site_path+'/morph/'):
               os.makedirs(site_path+'/morph/')
        morph=site_path+'/morph/'
        if not os.path.exists(site_path+'/motion/'):
               os.makedirs(site_path+'/motion/')
        motion=site_path+'/motion/'

	#get sweep

	print "geting sweep"
	for field, field_dic in radar1.fields.iteritems():
		get_sweep(radar1,field,sweep)
		get_sweep(radar2,field,sweep)

	#saving non masked data
	#display = pyart.graph.RadarDisplay(radar1)
	#for field, field_dic in radar1.fields.iteritems():
	#	geotiff2png.radarDisplay2geotiff(radar1,display,field+".tiff",field,0)

	# data quality control
	if maskin == 'radar':
                print "masking radar data"
                mask_ = filler_filter(radar1.fields['HCLASS2']['data'])
                mask_2 = filler_filter(radar2.fields['HCLASS2']['data'])
                for field in interpolated_variables:
                        if (field != "ROI"):# and (field != "HCLASS2"):         
                                radar1.fields[field]['data'] = np.ma.MaskedArray(radar1.fields[field]['data'].data*mask_,radar1.fields[field]['data'].mask)
                                radar2.fields[field]['data'] = np.ma.MaskedArray(radar2.fields[field]['data'].data*mask_2,radar2.fields[field]['data'].mask)
		radar1 = mask_radar(radar1)
		radar2 = mask_radar(radar2)

	
	# perform Cartesian mapping, limit to the reflectivity field.
	#grid1 = pyart.io.grid.read_grid("test_grid1.nfc")
	#grid2 = pyart.io.grid.read_grid("test_grid2.nfc")

	print "griding first file..."
	dist = radar1.range['data'][-1]
	rcells = radar1.ngates

	start_time = datetime.datetime.now()

	grid1 = pyart.map.grid_from_radars(
	    (radar1,),
	    grid_shape=(rcells, rcells, 2),
	    grid_limits=((dist, -dist), (dist, -dist),
		         (10, 10)),
	    fields=interpolated_variables,leafsize = 50)
        #grid1.write(images+RADAR_FILE1)

	print "griding second file..."
	grid2 = pyart.map.grid_from_radars(
	    (radar2,),
	    grid_shape=(rcells, rcells, 2),
	    grid_limits=((dist, -dist), (dist, -dist),
		         (10, 10)),
	    fields=interpolated_variables,leafsize = 50)
        #grid2.write(images+RADAR_FILE2)
	end_time = datetime.datetime.now()
	if log is not None:
		tmp = end_time-start_time
		log.write("Gridding time: " + str(tmp.seconds))

	#data Quality control
	if maskin == 'grid':
		grid1 = mask_grid(grid1)
		grid2 = mask_grid(grid2)

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
        print path
	for i in interpolated_variables:
		print "interpolating" + str(i) 
		image1 = images+RADAR_FILE1 +i+".png"
		image2 = images+RADAR_FILE2 +i+".png"
		vec1 = filename+"_motion-motion1.pdvm"
		vec2 = filename+"_motion-motion2.pdvm"

		args=path+"/optflow/build/bin/morph3 --image1 " +image1+" --image2 "+image2+" --numtimesteps "+str(timesteps)+ " --algorithm proesmans --outprefix " + filename+"_"+i + " --vec1 "+vec1+" --vec2 "+ vec2
		os.system(args)
        if not os.path.exists('motion'):
               os.makedirs('motion')
	print "making geotiffs"
	#step 3 make geotiff's from interpolated images
        
	for i in interpolated_variables:
		ifiles = glob.glob('*'+i+'*.png')
		for ifile in ifiles:
			ofile, ext = os.path.splitext(ifile)
			ofile = morph+ofile + ".tiff"
			geotiff2png.png2geotiff(ifile,i,ofile,grid1)
			os.remove(ifile)
        # Moving vector motion to the corresponding folder
        mfiles=glob.glob('*_motion-motion*')
        for mfile in mfiles:
                 print mfile
                 shutil.move(mfile,motion)

def main():
	RADAR_FILE1_path = '/home/Radar/annakaisa_data/KUM111210114433.RAW1J3D'
	RADAR_FILE2_path = '/home/Radar/annakaisa_data/KUM111210115015.RAW1J3F'
	timesteps=9
	#morph='/home/Radar/annakaisa_data/morp/'
	#images='/home/Radar/annakaisa_data/images/'
	morph="morp_annakaisa/"
	images="images_annakaisa/"
	filename='KUM114433-114831'
	interpolate(RADAR_FILE1_path,RADAR_FILE2_path,timesteps,images,morph,filename,0,['DBZ2','HCLASS2'])

#main()
