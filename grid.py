"""
pyart.io.grid
=============

Reading and writing Grid objects.

.. autosummary::
    :toctree: generated/

    read_grid
    write_grid

    _read_grid_cf
    _read_grid_wrf

.. autosummary::
    :toctree: generated/
    :template: dev_template.rst

    Grid

"""

from warnings import warn

import netCDF4

from .netcdf import _ncvar_to_dict, _create_ncvar
import sys, os, time
from scipy import ndimage
from scipy import misc
import scipy.io
from matplotlib.image import AxesImage
from pylab import *
import gdal,cmath
import numpy as np
import os

def read_grid(filename):
    """
    Read a netCDF grid file

    Parameters
    ----------
    filename : str
        Filename of netCDF grid file to read

    Returns
    -------
    grid : Grid
        Grid object containing Grid data.

    """
    ncobj = netCDF4.Dataset(filename, 'r')
    ncvars = ncobj.variables

    # metadata
    metadata = dict([(k, getattr(ncobj, k)) for k in ncobj.ncattrs()])

    # axes
    axes_keys = ['time', 'time_start', 'time_end',
                 'z_disp', 'y_disp', 'x_disp',
                 'alt', 'lat', 'lon']
    axes = dict((k, _ncvar_to_dict(ncvars[k])) for k in axes_keys)

    # read in the fields
    # determine the correct shape of the fields
    # ARM standard required a time dimension, so the shape of the fields
    # in the file are (1, nz, ny, nx) but the field data should be shaped
    # (nz, ny, nx) in the Grid object
    ncdims = ncobj.dimensions
    field_shape = tuple([len(ncdims[i]) for i in ['nz', 'ny', 'nx']])
    field_shape_with_time = (1, ) + field_shape  # 1, nz, ny, nx on disk

    # check all non-axes variables, those with the correct shape
    # are added to the field dictionary, if a wrong sized field is
    # detected a warning is raised
    field_keys = [k for k in ncvars.keys() if k not in axes_keys]
    fields = {}
    for field in field_keys:
        field_dic = _ncvar_to_dict(ncvars[field])
        if field_dic['data'].shape == field_shape_with_time:
            field_dic['data'].shape = field_shape
            fields[field] = field_dic
        else:
            bad_shape = field_dic['data'].shape
            warn('Field %s skipped, incorrect shape %s', (field, bad_shape))

    return Grid(fields, axes, metadata)

def write_grid_geotiff(filename,grid):
    """
	Write A Grid object to a GEOtiff file

	Parameters
	----------
	filename : str
		Filename to save grid to
	Grid : Grid
		Grid object to write
    """
    path,filename = os.path.split(filename)
    name, end = os.path.splitext(filename)
    for field, field_dic in grid.fields.iteritems():
	
	ofile = name + "_" + field+end
	if field != "ROI":
	    grid_shape = grid.fields[field]['data'].shape
	    nz, ny, nx = grid_shape
	    rcells = ny*0.5
	    dist = max(grid.axes['x_disp']['data'])
	    rangestep = grid.axes['x_disp']['data'][1] - grid.axes['x_disp']['data'][2]
	    print "dist :" + str(dist)
	    print "rcells :" + str(rcells)
	    print "rangestep :" + str(rangestep)
	    lat = grid.axes['lat']['data'][0]
	    lon = grid.axes['lon']['data'][0]
	    data =  grid.fields[field]['data'][0].data

 	    data[data == 0] = nan
	    data[data == -9999] = nan

	    out_driver = gdal.GetDriverByName("GTiff")
	    dst_options = ['COMPRESS=LZW','ALPHA=YES']
	    #print path+"/"+ofile
	    print str(ofile)
	    print "tset"
	    dst_ds = out_driver.Create(str(path+"/"+ofile), int(2*rcells), int(2*rcells), 1, gdal.GDT_Float32, dst_options)
	    dst_ds.SetGeoTransform( [ dist, -rangestep, 0, -dist, 0, rangestep ] )

	    iproj = 'PROJCS["unnamed",GEOGCS["WGS 84",DATUM["unknown",SPHEROID["WGS84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Azimuthal_Equidistant"],PARAMETER["latitude_of_center",'+str(lat)+'],PARAMETER["longitude_of_center",'+str(lon)+'],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'
	    dst_ds.SetProjection(iproj)

    	    dst_ds.GetRasterBand(1).WriteArray( data[::-1,:] )


def write_grid(filename, grid, format='NETCDF4'):
    """
    Write a Grid object to a CF-1.5 and ARM standard netcdf file

    Parameters
    ----------
    filename : str
        Filename to save grid to.
    grid : Grid
        Grid object to write.
    format : str, optional
        NetCDF format, one of 'NETCDF4', 'NETCDF4_CLASSIC',
        'NETCDF3_CLASSIC' or 'NETCDF3_64BIT'. See netCDF4 documentation for
        details.

    """
    ncobj = netCDF4.Dataset(filename, 'w', format=format)

    # create the time dimension
    ncobj.createDimension('time', None)

    # create additional dimensions
    grid_shape = grid.fields[grid.fields.keys()[0]]['data'].shape
    nz, ny, nx = grid_shape
    ncobj.createDimension('nz', nz)
    ncobj.createDimension('ny', ny)
    ncobj.createDimension('nx', nx)

    # axes variables
    if 'base_time' in grid.axes.keys():
        _create_ncvar(grid.axes['base_time'], ncobj, 'base_time', ())
    if 'time_offset' in grid.axes.keys():
        _create_ncvar(grid.axes['time_offset'], ncobj, 'time_offset',
                      ('time',))
    _create_ncvar(grid.axes['time'], ncobj, 'time', ('time', ))
    _create_ncvar(grid.axes['time_end'], ncobj, 'time_end', ('time', ))
    _create_ncvar(grid.axes['time_start'], ncobj, 'time_start', ('time', ))
    _create_ncvar(grid.axes['x_disp'], ncobj, 'x_disp', ('nx', ))
    _create_ncvar(grid.axes['y_disp'], ncobj, 'y_disp', ('ny', ))
    _create_ncvar(grid.axes['z_disp'], ncobj, 'z_disp', ('nz', ))
    _create_ncvar(grid.axes['lat'], ncobj, 'lat', ('time', ))
    _create_ncvar(grid.axes['lon'], ncobj, 'lon', ('time', ))
    _create_ncvar(grid.axes['alt'], ncobj, 'alt', ('time', ))

    # field variables
    for field, field_dic in grid.fields.iteritems():
        # append 1, to the shape of all data to indicate the time var.
        field_dic['data'].shape = (1, ) + field_dic['data'].shape
        _create_ncvar(field_dic, ncobj, field, ('time', 'nz', 'ny', 'nx'))
        field_dic['data'].shape = field_dic['data'].shape[1:]

    # metadata
    for k, v in grid.metadata.iteritems():
        setattr(ncobj, k, v)

    ncobj.close()
    return


def _read_grid_cf(filename):
    """
    Read a CF compliant netCDF file containing a grid.

    Parameters
    ----------
    filename : str
        Filename of the netCDF file.

    Returns
    -------
    grid : Grid
        Frid object containing data.

    Notes
    -----
    This function does only the most basic variable checking.  The resulting
    Grid object is most likely not writable.

    """
    ncobj = netCDF4.Dataset(filename)
    ncvars = ncobj.variables
    fields = {}
    axes = {}
    for var in ncvars:
        if len(ncvars[var].shape) > 1:
            # dimensionality of 2+ are fields variables
            fields[var] = _ncvar_to_dict(ncvars[var])
        else:
            # dimensionality of 1 are axes variables
            axes[var] = _ncvar_to_dict(ncvars[var])
    return Grid(fields, axes, {})


def _read_grid_wrf(filename):
    """
    Read a WRF netCDF file containing a grid.

    Parameters
    ----------
    filename : str
        Filename of the WRF netCDF file.

    Returns
    -------
    grid : Grid
        Grid object containing data.

    Notes
    -----
    This function does only the most basic variable checking.  The resulting
    Grid object is most likely not writable.

    """
    ncobj = netCDF4.Dataset(filename)
    ncvars = ncobj.variables
    fields = {}
    axes = {}
    for var in ncvars:
        if len(ncvars[var].shape) > 1:
            # dimensionality of 2+ are fields variables
            fields[var] = _ncvar_to_dict(ncvars[var])
        else:
            # dimensionality of 1 are axes variables
            axes[var] = _ncvar_to_dict(ncvars[var])
    return Grid(fields, axes, {})


class Grid:
    """
    An object for holding gridded Radar data.

    Parameters
    ----------
    fields : dict
        Dictionary of field dictionaries.
    axes : dict
        Dictionary of axes dictionaries.
    metadata : dict
        Dictionary of metadata.

    Attributes
    ----------
    fields: dict
        Dictionary of field dictionaries.
    axes: dict
        Dictionary of axes dictionaries.
    metadata: dict
        Dictionary of metadata.

    """
    def __init__(self, fields, axes, metadata):
        """ initalize """
        self.fields = fields
        self.metadata = metadata
        self.axes = axes
        return

    def write(self, filename, format='NETCDF4'):
        """
        Write the the Grid object to a netcdf file.

        Parameters
        ----------
        filename : str
            Filename to save to.
        format : str, optional
            NetCDF format, one of 'NETCDF4', 'NETCDF4_CLASSIC',
            'NETCDF3_CLASSIC' or 'NETCDF3_64BIT'. See netCDF4 documentation
            fordetails.

        """
	if(format == 'NETCDF4'):
        	write_grid(filename, self, format=format)
			
	if(format == 'GTiff'):
		write_grid_geotiff(filename,self)
