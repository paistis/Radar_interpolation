#!/bin/bash

rm kum.tif ker.tif

gdalwarp -t_srs "EPSG:4326" -of GTiff  KUM_1715_Z2_sweep1.tiff kum.tif 
gdalwarp -t_srs "EPSG:4326" -of GTiff  KER_Z2_sweep1.tiff ker.tif 

Rscript cmd.r


