#!/usr/bin/python

import radarlib as radar
import hdf5lib as hdf5

import sys, os, time

from scipy import ndimage
from scipy import misc

import scipy.io

from matplotlib.image import AxesImage
from pylab import *

import gdal,cmath
import numpy as np

def(ifile,isweep,var,dtime,otfile):

	if os.path.exists(ifile):
	    ppi = hdf5.HDF5scan(ifile,isweep,var,dtime)	
	    rcells = int(ppi.dist/ppi.rangestep)

	    lbm = np.zeros( (361., rcells) )
	    #mask 
	    mask = np.zeros( (361., rcells) )
	

	    lbm[:,:] = -999
	    mask[:,:] = -999
	
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

	    ilbm = rcoord.getCartesian(lbm)
	    mask = rcoord.getCartesian(mask)


	    #convert values to 8-bit
	    ilbm = np.asarray(ilbm)
	    if (var == 'Z2'):
		ilbm[ilbm >= 95.5] = nan
		ilbm[ilbm < -31.5] = nan
	    if (var == 'KDP2'):
		ilbm[ilbm <= -30.00] = nan
		ilbm[ilbm >= 28.51] = nan

	    if (var == 'RHOHV2'):
		ilbm[ilbm<=0] = nan
		ilbm[ilbm>1] = nan)

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

	else:
	    print "File " + ifile + " non disponibile"

