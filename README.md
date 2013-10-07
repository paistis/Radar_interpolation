Radar_interpolation
===================
Using
sh ./interpolate.sh config.sh

#example config file

#input hdf5 files
file1="/home/nordlikg/fmi/HDF5/20100808/VAN/201008081800_VAN.PPI1_A.raw.h5_with_rayHdrs_F.h5"
file2="/home/nordlikg/fmi/HDF5/20100808/VAN/201008081815_VAN.PPI1_A.raw.h5_with_rayHdrs_F.h5"

#time step variable etc
timesteps=16
var="Z2"
sweep=2
site="VAN"

#output folder's for output images and interpolated images
images="images/"
morp_output="morp/" #output forder for interpolated images

#these are optional, and theses sould not be defined if they are not used
vec1="motion1.pvdm"
vec2="motion2.pvdm"
