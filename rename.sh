#!/usr/bin/bash

#Data source directory
SRCD="/home/Radar/data/RAW/KUM/2013-08-14/"

# Directory where the renaming script is located 
SCRD1="/home/Radar/Radar_interpolation_lcr/Radar_interpolation/"
scr="rename.py"

cd $SRCD
# file mask
srcfile=*

for i in $(ls -d -1 $PWD/*.* *$srcfile*);
do
        src=$i
        tgtfile=$src
        echo 'working on '$tgtfile
        echo '.............'
        echo  $tgtfile 
        python $SCRD1$scr $tgtfile
done

echo 'Done !!!'
