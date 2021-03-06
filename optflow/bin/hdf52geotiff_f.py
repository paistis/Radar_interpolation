#!/usr/bin/python

import radarlib as radar
#import irislib as iris
import hdf5lib as hdf5

import sys, os, time

from scipy import ndimage
from scipy import misc

import scipy.io

from matplotlib.image import AxesImage
from pylab import *

import gdal,cmath
import numpy as np

# MAIN
#print os.environ["MEASURMENT_VAR"]
#raw_input("Press anykey...")
try:
    ifile = sys.argv[1]
    isweep = int(sys.argv[2])
    var = sys.argv[3]
    dtime = sys.argv[4]
    otfile = sys.argv[5] 
  
except:
    print "usage iris_ppi.py [matlab ppi] [n sweep] [var] [dtime] [otfile]"
    print "sweeps start from 0 and units are in m"
    print 'var = ["zt_dbz", "zh_dbz","v_mps","w_mps","zdr_db","phidp_deg","rhohv","sqi","kdp_degpkm","zhc_dbz","zdrc_db"]'
    os._exit(0)

if os.path.exists(ifile):

    #ppi = iris.IRISscan(ifile, isweep, var, dtime)
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
	    #print "i" + str(i)
	    #print "j" + str(j)
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
    #clean mask data
    #mask[mask >= 95.5] = nan
    #mask[maks < -31.5] = nan
    maks = np.piecewise(mask,[mask>0,mask<=0],[lambda mask: (((mask*126)/(0.25*600))+129),lambda mask: (((mask*126)/(-0.25*600))-127)*-1])
    mask[mask <= 0] = nan
    mask[mask >= 255] = nan
    np.savetxt('mask.txt',mask)
    print "ilbm"

    #convert values to 8-bit
    ilbm = np.asarray(ilbm)
    if (var == 'Z2'):
	#select dynamic range
	ilbm[ilbm >= 95.5] = nan
	ilbm[ilbm < -31.5] = nan
	#ilbm = np.round((2*ilbm+64))
    if (var == 'KDP2'):
        ilbm[ilbm <= -30.00] = nan
	ilbm[ilbm >= 28.51] = nan
	#ilbm = np.piecewise(ilbm,[ilbm>0,ilbm<=0],[lambda ilbm: (((ilbm*126)/(0.25*600))+129),lambda ilbm: (((ilbm*126)/(-0.25*600))-127)*-1])
	#ilbm[ilbm == 0] = nan
	#ilbm[ilbm == 255] = nan
	#ilbm = np.round(ilbm)
    if (var == 'RHOHV2'):
	ilbm[ilbm<=0] = nan
	ilbm[ilbm>1] = nan
	#ilbm = np.multiply(ilbm,ilbm)*253+1
    ilbm[mask==nan] = nan	
    asp = 1.0
    np.savetxt('dump_Data.txt',ilbm)
    cmap = cm.get_cmap('jet', 256)

    norm = cm.colors.Normalize(vmin=nanmin(ilbm[:,:]), vmax=nanmax(ilbm[:,:]))

#    im = plt.imshow(ilbm[:,:], aspect = asp, cmap=cmap,norm = norm, interpolation='nearest',extent=([ - ppi.dist / 1000., ppi.dist / 1000., - ppi.dist / 1000., ppi.dist / 1000.]))

#    title(rname[0,0][0] + "\nlat = " + str(round(lat,3)) + " lon = " + str(round(lon,3)) + " Elev = " + str(round(float(posangle[0,isweep][0]),2)),fontsize = 12)

#    colorbar(orientation='horizontal')

#    ylabel('Distance [km]', fontsize = 10)
#    xlabel('Distance [km]', fontsize = 10)

#    grid(True)

#<    show()

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

    if len(sys.argv) > 6 and sys.argv[6][1] == 'r':

        projfile = 'PPI' + ('%03d'% round(10*float(ppi.posangle[0,isweep][0]),0)) + '_' + var.upper() + '_' + otfile

        os.system("gdalwarp -co \"COMPRESS=LZW\" -t_srs \"epsg:3067\" %s %s" % (otfile, projfile))

        indataset = gdal.Open(projfile, gdal.GA_Update)

        if indataset == None:
           print('Cannot open', projfile)
           sys.exit(2)

        band = indataset.GetRasterBand(1)

        if band == None:
           print('Cannot load band', iBand, 'from the', infile)
           sys.exit(2)

        rain = band.ReadAsArray(0, 0)

        rain[rain == 0] = nan

        rain[:,:] = rain[:,:] - offset

        indataset.GetRasterBand(1).WriteArray( rain[:,:] )

        indataset.SetMetadataItem("RADAR",str(ppi.rname))
        indataset.SetMetadataItem("LAT", str(ppi.lat))
        indataset.SetMetadataItem("LON", str(ppi.lon))
        indataset.SetMetadataItem("ALT", str(ppi.alt))
        indataset.SetMetadataItem("ELEV", str(float(ppi.posangle[0])))
        indataset.SetMetadataItem("VARIABLE",var)
        indataset.SetMetadataItem("VOL_NAME",str(ppi.scan))
        indataset.SetMetadataItem("DATETIME", dtime)

        indataset = None

else:
    print "File " + ifile + " non disponibile"

