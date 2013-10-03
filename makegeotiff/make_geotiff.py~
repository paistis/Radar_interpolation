import radarlib as radar
import hdf5lib as hdf5

import sys, os, time

from scipy import misc
import numpy
import scipy.io
import scipy.signal
import Image
from matplotlib.image import AxesImage
from pylab import *
import numpy as np
import gdal,cmath

#This script converts png to geotiff, coordinate system comes form original HDF5 file. Based on robertos code. png images are 8-bit gray scale
#8-bit integer values are converted back to physical values only for Z2,KDP2,RHOHV values

def main():
	otfile = sys.argv[3]
	img_file = sys.argv[1]
	ifile = sys.argv[2]
	#read Z2 data from refrence hdf5 file
	isweep = 1
	var = os.environ['MEASURMENT_VAR'] #get measurmetn varible, set in interpolate.sh
	
	#open original hdf5 file for 
	ppi = hdf5.HDF5scan(ifile,isweep,var)	
	rcells = int(ppi.dist/ppi.rangestep)
	dtime=ppi.dtime
	lbm = np.zeros( (361., rcells) )

	lbm[:,:] = -999
	#data to radar coordinate system.
	rcoord = radar.RadarCoordinateSystem(ppi.lat, ppi.lon, ppi.alt)
	#read data to matrix
	for k in range(ppi.az.size):
	   for i in range(rcells):

		j = int(round(ppi.az[k]))
		if lbm[j,i] == -999:
		 		r,h = rcoord.getSlantRangeElevation( i * ppi.rangestep, ppi.posangle[k])

				idx = int(r / ppi.rangestep )

				if  (idx < ppi.bins):
	  				lbm[j,i] = ppi.obsval[k,idx]
				else:
					break
	#clean rest of data
	lbm[lbm == -999] = 0
	lbm[lbm == -327] = 0
	lbm[lbm == 327] = 0

	min_ = np.min(lbm)
	max_ = np.max(lbm)

	ilbm = rcoord.getCartesian(lbm)
	if (var == 'Z2'):
		print 'Appying offset...'
		offset = 1000.0
	else:
		offset = 0.0

	ilbm[:,:] = ilbm[:,:] + offset
	nx_d,ny_d = ilbm.shape
	#load png image to matrix
    	Img = misc.imread(img_file)
    	arr = numpy.asarray(Img)
	lbm2=Img

	lbm2 = lbm2.astype(float)
	#convert values to physical values
	if (var =='Z2'):
		lbm2[lbm2 >= 65534] = nan
		lbm2[lbm2 <= 1] = nan
		lbm2 = (lbm2-32768.0)/100.0
		lbm2[lbm2 >= 327.66] = nan
   		lbm2[lbm2 <= -325.00] = nan

	if (var =='KDP2'):
		lbm2[lbm2 >= 65534] = nan
		lbm2[lbm2 <= 1] = nan
		lbm2 = (lbm2-32768.0)/100.0
		lbm2[lbm2 >= 327.66] = nan
   		lbm2[lbm2 <= -325.00] = nan

	if (var =='V2'):
		lbm2[lbm2 >= 65534] = nan
		lbm2[lbm2 <= 1] = nan
		lbm2 = (lbm2-32768.0)/100.0
		lbm2[lbm2 >= 327.66] = nan
   		lbm2[lbm2 <= -325.00] = nan

	if (var =='RHOHV2'):
		lbm2[lbm2 >= 65534] = nan
		lbm2[lbm2 <= 1] = nan
		lbm2 = (lbm2-32768.0)/100.0
		lbm2[lbm2 >= 327.66] = nan
   		lbm2[lbm2 <= -325.00] = nan
	

	nx,ny = arr.shape

	del_x = ((nx-nx_d)/2.0)
	del_y = ((ny-ny_d)/2.0)
	lbm3 = lbm2[del_x:nx_d+del_x,del_y:ny_d+del_y]
	#write geotiff
	format = "GTiff"
    	dst_options = ['COMPRESS=LZW','ALPHA=YES']

    	out_driver = gdal.GetDriverByName(format)
    	dst_ds = out_driver.Create( otfile, nx_d, ny_d, 1, gdal.GDT_Float32, dst_options)

    	dst_ds.SetGeoTransform( [ -ppi.dist, ppi.rangestep, 0, ppi.dist, 0, -ppi.rangestep ] )

	iproj = 'PROJCS["unnamed",GEOGCS["WGS 84",DATUM["unknown",SPHEROID["WGS84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Azimuthal_Equidistant"],PARAMETER["latitude_of_center",'+str(ppi.lat)+'],PARAMETER["longitude_of_center",'+str(ppi.lon)+'],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'

    	dst_ds.SetProjection(iproj)

    	dst_ds.GetRasterBand(1).WriteArray(lbm3[:,:] )
    	dst_ds.SetMetadataItem("RADAR","test")
    	dst_ds.SetMetadataItem("LAT", str(ppi.lat))
    	dst_ds.SetMetadataItem("LON", str(ppi.lon))
    	dst_ds.SetMetadataItem("ALT", str(ppi.alt))
    	dst_ds.SetMetadataItem("ELEV", str(float(ppi.posangle[0])))
    	dst_ds.SetMetadataItem("VARIABLE",var)
    	dst_ds.SetMetadataItem("VOL_NAME",ppi.scan)
    	dst_ds.SetMetadataItem("DATETIME", dtime)

    	dst_ds = None


main()
