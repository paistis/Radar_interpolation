#!/usr/bin/python
import sys, os, time
from scipy import ndimage
from scipy import misc
import scipy.io
from matplotlib.image import AxesImage
from pylab import *
import gdal,cmath
import numpy as np
import matplotlib.pyplot as plt
import Image
import pyart
import cmath, math
import datetime
import shutil

# MAIN
def radar_info(radar):
	
	site = radar.metadata['instrument_name']
	site = site[0:3]
	site = site.upper()
	
	scan_type = radar.scan_type	

	time = radar.time['units']
	time = time.split(' ')
	time = time[-1]
	time= datetime.datetime.strptime(time,'%Y-%m-%dT%H:%M:%SZ')
		
	output = {'site': site,'time':time,'scan_type': scan_type}
	return output

def rename_file(filename):
	radar = pyart.io.read_sigmet(filename,sigmet_field_names=True, time_ordered='none')
	info = radar_info(radar)
	new_name = info['time'].strftime("%Y%m%d%H%M%S")+"_"+info['site']+"_"+info['scan_type']+".raw"		
	path = os.path.dirname(filename)	
        shutil.move(filename,path+"/"+new_name)
def geotiff2png(ifile,var,ofile,bit8=False):
	if var=='DBZ2':
		var = 'reflectivity_horizontal'
	if var=='KDP2':
		var = 'diff_phase'
	if var=='RHOHV2':
		var='copol_coeff'
	if var=='VEL2':
		var='mean_doppler_velocity'
	if os.path.exists(ifile):
	    ds = gdal.Open(ifile)
	    ilbm = ds.GetRasterBand(1).ReadAsArray()
	    h,w = ilbm.shape
	    size = int(2**(ceil(log(max(w,h))/log(2))))
	    if (var == 'reflectivity_horizontal'):
		
		if(bit8 == True):
			#8bit data
			ilbm[ilbm >= 95.5] = nan
			ilbm[ilbm < -31.5] = nan
			ilbm = np.round((2.0*ilbm+64.0))
			ilbm = ilbm.astype('int8')
			img = scipy.misc.toimage(ilbm)
			img = img.resize((size,size))
			img.save(ofile)
			return 0

		ilbm[ilbm >= 327.66] = nan
	   	ilbm[ilbm <= -327.67] = nan
		ilbm = np.round((100.0*ilbm+32768.0))
	    #KDP2 from sigmet.py
	    if (var == "diff_phase"):
		ilbm = np.round(100.0*ilbm+32768)
		ilbm[ilbm <= 0] = nan
		ilbm[ilbm >= 65535] = nan
	    #RHOHV2 from sigmet.py
	    if (var == "copol_coeff"):
		ilbm = np.round((ilbm*65533)+1)
		ilbm[ilbm <= 0] = nan
		ilbm[ilbm >= 65535] = nan

	    if (var == "mean_doppler_velocity"):
		ilbm = np.round(100.0*ilbm+32768)
		ilbm[ilbm <= 0] = nan
		ilbm[ilbm >= 65535] = nan

	    ilbm = ilbm.astype('int32')
	    img = scipy.misc.toimage(ilbm,high=np.max(ilbm),low=np.min(ilbm),mode='I')
	    img = img.resize((size,size))
	    img.save(ofile)
	else:
	    print "File " + ifile+ " does not exist"

def png2geotiff(ifile,var,ofile,grid):

	grid_shape = grid.fields[var]['data'].shape
	nz, ny, nx = grid_shape
	rcells = ny*0.5
	dist = max(grid.axes['x_disp']['data'])
	rangestep = grid.axes['x_disp']['data'][1] - grid.axes['x_disp']['data'][2]
    	lat = grid.axes['lat']['data'][0]
	lon = grid.axes['lon']['data'][0]

	grid_shape = grid.fields[var]['data'].shape
	nz_d, ny_d, nx_d = grid_shape

    	Img = misc.imread(ifile)
    	arr = np.asarray(Img)
	lbm2=Img
	if var=='DBZ2':
		var = 'reflectivity_horizontal'
	if var=='KDP2':
		var = 'diff_phase'
	if var=='RHOHV2':
		var='copol_coeff'
	if var == 'VEL2':
		var='mean_doppler_velocity'
	if (var =='reflectivity_horizontal'):
		#lbm2[lbm2 >= 65534] = nan
		#lbm2[lbm2 <= 1] = nan
		lbm2 = (lbm2-32768.0)/100.0
		lbm2[lbm2 >= 327.66] = nan
   		lbm2[lbm2 <= -325.00] = nan

	if (var =='diff_phase'):
		#lbm2[lbm2 >= 65534] = nan
		#lbm2[lbm2 <= 1] = nan
		lbm2 = (lbm2-32768.0)/100.0
		lbm2[lbm2 >= 327.66] = nan
   		lbm2[lbm2 <= -325.00] = nan

	if (var =='mean_doppler_velocity'):
		#lbm2[lbm2 >= 65534] = nan
		#lbm2[lbm2 <= 1] = nan
		lbm2 = (lbm2-32768.0)/100.0
		lbm2[lbm2 >= 327.66] = nan
   		lbm2[lbm2 <= -325.00] = nan

	if (var =='copol_coeff'):
		#lbm2[lbm2 >= 65534] = nan
		#lbm2[lbm2 <= 1] = nan
		lbm2 = (lbm2-32768.0)/100.0
		lbm2[lbm2 >= 327.66] = nan
   		lbm2[lbm2 <= -325.00] = nan

	nx,ny = arr.shape

	del_x = ((nx-nx_d)/2.0)
	del_y = ((ny-ny_d)/2.0)
	lbm3 = lbm2[del_x:nx_d+del_x,del_y:ny_d+del_y]

	out_driver = gdal.GetDriverByName("GTiff")
	dst_options = ['COMPRESS=LZW','ALPHA=YES']
	dst_ds = out_driver.Create(ofile, int(2*rcells), int(2*rcells), 1, gdal.GDT_Float32, dst_options)
	dst_ds.SetGeoTransform( [ dist, -rangestep, 0, -dist, 0, rangestep ] )

	iproj = 'PROJCS["unnamed",GEOGCS["WGS 84",DATUM["unknown",SPHEROID["WGS84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Azimuthal_Equidistant"],PARAMETER["latitude_of_center",'+str(lat)+'],PARAMETER["longitude_of_center",'+str(lon)+'],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'
	dst_ds.SetProjection(iproj)

    	dst_ds.GetRasterBand(1).WriteArray( lbm3)

def getCartesian(indata ):

	(dimy, dimx) = indata.shape

        pcart = zeros( (2 * dimx, 2 * dimx) )
        pcart[:,:] = nan

        for x in range(-dimx, dimx):
        	for y in range(-dimx, dimx):

            		z = complex(x + 0.5, y + 0.5)

            		p = cmath.polar(z)

            		if p[0] < dimx:
                  		pcart[x + dimx,y + dimx] = indata[int(180. / pi * p[1] * dimy / 360.),int(p[0])]
	return pcart

def radarDisplay2geotiff(radar,ofile,field,tilt):	

	#test
	display = pyart.graph.RadarDisplay(radar)
	data = display._get_data(field, tilt, None)
        x, y = display._get_x_y(field, tilt)
    	#ax = plt.gca()
	#pm = ax.pcolormesh(x,y,data)
	#plt.show()	
	data = getCartesian(data)

	dist = radar.range['data'][-1]
	rcells = radar.ngates
	rangestep = radar.range['data'][1] - radar.range['data'][0]

    	lat = radar.latitude
	lon = radar.longitude

	out_driver = gdal.GetDriverByName("GTiff")
	dst_options = ['COMPRESS=LZW','ALPHA=YES']
	dst_ds = out_driver.Create(ofile, int(2*rcells), int(2*rcells), 1, gdal.GDT_Float32, dst_options)
	dst_ds.SetGeoTransform( [ dist, -rangestep, 0, -dist, 0, rangestep ] )
	iproj = 'PROJCS["unnamed",GEOGCS["WGS 84",DATUM["unknown",SPHEROID["WGS84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Azimuthal_Equidistant"],PARAMETER["latitude_of_center",'+str(lat)+'],PARAMETER["longitude_of_center",'+str(lon)+'],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'
	dst_ds.SetProjection(iproj)
    	dst_ds.GetRasterBand(1).WriteArray( data[:,::-1] )

