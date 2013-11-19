#!/usr/bin/python

import pyproj as proj4 
import cmath, math
from numpy import *
from PIL import Image, ImageDraw, ImageChops, ImageFilter
from scipy import ndimage

#import h5py
#from numpy.linalg import norm

#import sys, os, time

######################################################################################################################
#
#	Classe per la gestione di slant range, height
#

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
class RadarCoordinateSystem():

    """
        Converts spherical (range, az, el) radar coordinates to lat/lon/alt, and then to ECEF.
        
        An earth's effective radius of 4/3 is assumed to correct for atmospheric refraction.
    """
    
    def __init__(self, ctrLat, ctrLon, ctrAlt, datum='WGS84', ellps='WGS84', effectiveRadiusMultiplier=4./3.):
        self.ctrLat = float(ctrLat)
        self.ctrLon = float(ctrLon)
        self.ctrAlt = float(ctrAlt)
        self.datum=datum
        self.ellps=ellps
        
        self.lla = proj4.Proj(proj='latlong', ellps=self.ellps, datum=self.datum)
        self.xyz = proj4.Proj(proj='geocent', ellps=self.ellps, datum=self.datum)
        
        self.Requator, foo1, foo2 = proj4.transform(self.lla,self.xyz,0,0,0) # Equatorial radius  - WGS-84 value = 6378137.0
        foo1, foo2, self.Rpolar = proj4.transform(self.lla,self.xyz,0,90,0) # Polar radius  - WGS-84 value = 6356752.314
        self.flattening = (self.Requator-self.Rpolar)/self.Requator
        
        self.eccen = (2.0-self.flattening)*self.flattening   # First eccentricity squared - WGS-84 value = 0.00669437999013
        self.effectiveRadiusMultiplier = effectiveRadiusMultiplier
            
    def getGroundRangeHeight(self, r, elevationAngle):
        """Convert slant range (along the beam) and elevation angle into 
        ground range (great circle distance) and height above the earth's surface
        Follows Doviak and Zrnic 1993, eq. 2.28."""
    
        #Double precison arithmetic is crucial to proper operation.
        lat = self.ctrLat * pi / 180.0
        elev = array(elevationAngle * pi / 180.0, dtype='float64')
        slantr = array(r, dtype='float64')
        
        #figure out earth's radius at radar's lat ... non-spherical earth model
        e2 = self.eccen           # First eccentricity squared - WGS-84 value = 0.00669437999013
        a = self.Requator         # Equatorial radius  - WGS-84 value = 6378137.0
        Rearth = a/sqrt(1-e2*(sin(lat))**2) # radius of curvature
        
        Rprime = self.effectiveRadiusMultiplier * self.Requator
        
        # Eqns 2.28b,c in Doviak and Zrnic 1993
        # Radar altitude is tacked on at the end, which isn't part of their derivation. At 100 km, it's 
        #   worth < 10 m range error total for a radar at 500 m MSL. For 250 m gate spacing (typical at S-band), 
        #   this is not too important.
        h = sqrt(slantr**2.0 + Rprime**2.0 + 2*slantr*Rprime*sin(elev)) - Rprime
        s = Rprime * arcsin( (slantr*cos(elev)) / (Rprime + h) )
        
        h += self.ctrAlt
        
        return s, h 
        
    def getSlantRangeElevationHeight(self, groundRange, z):
        """Convert ground range (great circle distance) and height above 
        the earth's surface to slant range (along the beam) and elevation angle.
        Follows Doviak and Zrnic 1993, eq. 2.28"""
        
        lat = self.ctrLat * pi / 180.0
 
        #figure out earth's radius at radar's lat ... non-spherical earth model
        e2 = self.eccen           # First eccentricity squared - WGS-84 value = 0.00669437999013
        a = self.Requator         # Equatorial radius  - WGS-84 value = 6378137.0
        Rearth = a/sqrt(1-e2*(sin(lat))**2) # radius of curvature
        
        Rprime = self.effectiveRadiusMultiplier * self.Requator
        
        h = array(z - self.ctrAlt, dtype='float64')
        s = array(groundRange, dtype='float64')
        
        # Use law of cosines (Side-Angle-Side triangle theorem) with 
        # R', R'+h as sides and s/R' as the angle to get slant range
        r  = sqrt(Rprime**2.0 + (Rprime+h)**2.0 - 2*(Rprime+h)*Rprime*cos(s/Rprime))
        # Inverse of eq. 2.28c in Doviak and Zrnic 1993
        # Will return NaN for r=0
        el = arccos((Rprime+h) * sin(s/Rprime) / r) 
        el *= 180.0 / pi
        
        return r, el
            
    def getSlantRangeElevation(self, groundRange, el):
        """Convert ground range (great circle distance) and height above 
        the earth's surface to slant range (along the beam) and elevation angle.
        Follows Doviak and Zrnic 1993, eq. 2.28"""
        
        lat = self.ctrLat * pi / 180.0
        theta = el * pi / 180.0
 
        #figure out earth's radius at radar's lat ... non-spherical earth model
        e2 = self.eccen           # First eccentricity squared - WGS-84 value = 0.00669437999013
        a = self.Requator         # Equatorial radius  - WGS-84 value = 6378137.0
        Rearth = a/sqrt(1-e2*(sin(lat))**2) # radius of curvature
        
        # Inverse of eq. 2.28b in Doviak and Zrnic 1993
        # Inverse of eq. 2.28c in Doviak and Zrnic 1993

        Rprime = self.effectiveRadiusMultiplier * self.Requator

        s = array(groundRange, dtype='float64')

        h = Rprime * ( math.cos(theta) / math.cos( theta + s / Rprime) - 1)

        r = (Rprime + h) * math.sin(s / Rprime) / math.cos(theta);

        # Use law of cosines (Side-Angle-Side triangle theorem) with 
        # R', R'+h as sides and s/R' as the angle to get slant range
        #r  = sqrt(Rprime**2.0 + (Rprime+h)**2.0 - 2*(Rprime+h)*Rprime*cos(s/Rprime))
        # Will return NaN for r=0
        #el = arccos((Rprime+h) * sin(s/Rprime) / r) 
        #el *= 180.0 / pi
        
        return r,h

    def getCartesian(self, indata ):

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

