#!/usr/bin/python
#this program converts hdf5 files to ppi geotiff, code is base Robertos code.
#import radarlib as radar
#import hdf5lib as hdf5
import sys, os, time
sys.path.append( os.getcwd() + '/lib')

import radarlib as radar
import hdf5lib as hdf5
from scipy import ndimage
from scipy import misc

import scipy.io

from matplotlib.image import AxesImage
from pylab import *

import gdal,cmath
import numpy as np

# MAIN

def main(ifile,isweep,var,otfile,bit8=True):

	if os.path.exists(ifile):
	    image_folder = os.environ['IMAGE_FOLDER']
	    ppi = hdf5.HDF5scan(ifile,isweep,var)
	    dtime = ppi.dtime	
	    rcells = int(ppi.dist/ppi.rangestep)
	    #matrix of zeros from image
	    lbm = np.zeros( (361., rcells) )
	    #mask for removing clutters 
	    mask = np.zeros( (361., rcells) )
	
	    #fill matriec with some arbitary value(value -999 does not accure on measurments)	
	    lbm[:,:] = -999
	    mask[:,:] = -999
	    #data to radar coordinate system.
	    rcoord = radar.RadarCoordinateSystem(ppi.lat, ppi.lon, ppi.alt)
	    for k in range(ppi.az.size):
	   	for i in range(rcells):

		    j = int((ppi.az[k]))
		    if lbm[j,i] == -999:
		 		r,h = rcoord.getSlantRangeElevation( i * ppi.rangestep, ppi.posangle[k])

				idx = int(r / ppi.rangestep )

				if  (idx < ppi.bins):
	  				lbm[j,i] = ppi.obsval[k,idx]
					mask[j,i] = ppi.mask[k,idx]
				else:
					break

	    lbm[lbm == -999] = nan
	    mask[mask == -999] = nan
            masked=radar.filler_filter(mask)
            masked1=radar.median_filter(mask)
	    masked2=radar.closing_filter(mask)
            np.savetxt('Hclass_filled.txt',masked)
            np.savetxt('Hclass_median.txt',masked1)
            np.savetxt('Hclass_closing.txt',masked2)
            np.savetxt('Data.txt',lbm)
	    ilbm = rcoord.getCartesian(lbm)
            np.savetxt('Data_rcoord.txt',lbm)
	    mask = rcoord.getCartesian(masked)
            h_class = rcoord.getCartesian(mask)
            np.savetxt('Hclass_mask_rcood.txt',mask)
            np.savetxt('Hclass_rcood.txt',h_class)
	    ilbm_8bit = ilbm

	    print "ilbm"
	    if (var == 'Z2'):
		ilbm[ilbm >= 327.66] = nan
	   	ilbm[ilbm <= -327.67] = nan
		ilbm = np.round((100.0*ilbm+32768.0))
		
		if(bit8 == False):
			#8bit data
			ilbm_8bit[ilbm_8bit >= 95.5] = nan
			ilbm_8bit[ilbm_8bit < -31.5] = nan
			ilbm_8bit = np.round((2.0*ilbm_bit+64.0))

	    if (var == "KDP2"):
		ilbm = np.round(100.0*ilbm+32768)
		ilbm[ilbm <= 0] = nan
		ilbm[ilbm >= 65535] = nan
	    
	    if (var == "RHOVH2"):
		ilbm = np.round((ilbm*65533)+1)
		ilbm[ilbm <= 0] = nan
		ilbm[ilbm >= 65535] = nan

	    if (var == "V2"):
		ilbm = np.round(100.0*ilbm+32768)
		ilbm[ilbm <= 0] = nan
		ilbm[ilbm >= 65535] = nan

	    ilbm = np.asarray(ilbm)
 #           np.savetxt('Data.txt',ilbm)
            ilbm=ilbm*mask
           
 #          np.savetxt('Data_filter.txt',ilbm)	

	    #write Geotiff image 16bit
	    otfile2 = "8bit_"+otfile
	    otfile = os.getcwd()+ "/" + image_folder +otfile
	    format = "GTiff"
	    dst_options = ['COMPRESS=LZW','ALPHA=YES']

	    out_driver = gdal.GetDriverByName(format)
	    dst_ds = out_driver.Create( otfile, 2 * rcells, 2 * rcells, 1, gdal.GDT_Float32, dst_options)

	    dst_ds.SetGeoTransform( [ -ppi.dist, ppi.rangestep, 0, ppi.dist, 0, -ppi.rangestep ] )

	    iproj = 'PROJCS["unnamed",GEOGCS["WGS 84",DATUM["unknown",SPHEROID["WGS84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Azimuthal_Equidistant"],PARAMETER["latitude_of_center",'+str(ppi.lat)+'],PARAMETER["longitude_of_center",'+str(ppi.lon)+'],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'

	    dst_ds.SetProjection(iproj)

	    dst_ds.GetRasterBand(1).WriteArray( ilbm[::-1,:] )

	    dst_ds.SetMetadataItem("RADAR",str(ppi.rname))
	    dst_ds.SetMetadataItem("LAT", str(ppi.lat))
	    dst_ds.SetMetadataItem("LON", str(ppi.lon))
	    dst_ds.SetMetadataItem("ALT", str(ppi.alt))
	    dst_ds.SetMetadataItem("ELEV", str(float(ppi.posangle[0])))
	    dst_ds.SetMetadataItem("VARIABLE",var)
	    dst_ds.SetMetadataItem("VOL_NAME",str(ppi.scan))
	    dst_ds.SetMetadataItem("DATETIME", dtime)

	    dst_ds = None
	    #8bit
	    format = "GTiff"
	    dst_options = ['COMPRESS=LZW','ALPHA=YES']
	    otfile2 = os.getcwd()+"/" + image_folder +otfile2

	    out_driver = gdal.GetDriverByName(format)
	    dst_ds = out_driver.Create( otfile2, 2 * rcells, 2 * rcells, 1, gdal.GDT_Float32, dst_options)

	    dst_ds.SetGeoTransform( [ -ppi.dist, ppi.rangestep, 0, ppi.dist, 0, -ppi.rangestep ] )

	    iproj = 'PROJCS["unnamed",GEOGCS["WGS 84",DATUM["unknown",SPHEROID["WGS84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Azimuthal_Equidistant"],PARAMETER["latitude_of_center",'+str(ppi.lat)+'],PARAMETER["longitude_of_center",'+str(ppi.lon)+'],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'

	    dst_ds.SetProjection(iproj)

	    dst_ds.GetRasterBand(1).WriteArray( ilbm[::-1,:] )

	    dst_ds.SetMetadataItem("RADAR",str(ppi.rname))
	    dst_ds.SetMetadataItem("LAT", str(ppi.lat))
	    dst_ds.SetMetadataItem("LON", str(ppi.lon))
	    dst_ds.SetMetadataItem("ALT", str(ppi.alt))
	    dst_ds.SetMetadataItem("ELEV", str(float(ppi.posangle[0])))
	    dst_ds.SetMetadataItem("VARIABLE",var)
	    dst_ds.SetMetadataItem("VOL_NAME",str(ppi.scan))
	    dst_ds.SetMetadataItem("DATETIME", dtime)

	    dst_ds = None



	else:
	    print "File " + ifile + " non disponibile"

ifile = sys.argv[1]
isweep = int(sys.argv[2])
var = sys.argv[3]
otfile = sys.argv[4] 

main(ifile,isweep,var,otfile,bit8=True)

