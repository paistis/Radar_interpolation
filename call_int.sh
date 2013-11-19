#!/usr/bin/bash

# Data source directory
SRCD="/home/lrojas/Documents/Research/Urban_Rainfall/Data/HDF5/VAN/2013-08-14/"

# Directory where the interpolation script is located 
SCRD="/home/lrojas/Documents/Research/Urban_Rainfall/Radar_Git_Dev/Radar_interpolation/"

# Directory where the raw to hdf5 converter script is located 
SCRD1="/home/lrojas/Documents/Research/Urban_Rainfall/URCA/"

scr="interpolate.sh"
# RAW to Hdf5 data format conversion
# scr1="iris2hdf.sh" 

int=5
num=$((60/$int))
sweep=1
site1="VAN_20130814"
var="Z2"
date="20130814"
int=$(($int+1))
flag_int=1

#echo 'RAW to tiff convertion' (if needed: modify iris2hdf.sh script)
#bash $SCRD1$scr1
if test $flag_int -eq 1;then
 mask=*2013081412*PPI1_A*.h5
 mask2=*2013081412*PPI2_A*.h5
 mask3=*2013081412*PPI3_A*.h5
 mask4=*201308141300*PPI1_A*.h5
#cp $mask  $TGTD1
 fileLas=($(ls $SRCD$mask4))
 fileIni=($(ls $SRCD$mask))
 fileArray=("${fileIni[@]}" "${fileLas[@]}")
 fileArray2=($(ls $SRCD$mask2)) 
 fileArray3=($(ls $SRCD$mask3))
# get length of an array
 tLen=${#fileArray[@]}
 tLen=$((tLen-1))
 cd $SCRD
 sed -i "/timesteps/c\timesteps=$int" config.test
 sed -i "/var/c\var=$var" config.test
 sed -i "/sweep/c\sweep=$sweep" config.test

 # use for loop read all filenames
 for (( i=0; i<${tLen}; i++ ));
 do
   file1=${fileArray[$i]}
   if test $num -eq 12 ;then
      file2=${fileArray2[$i]}
      file3=${fileArray3[$i]}
      file4=${fileArray[$((i+1))]}
      echo "$file1"
      echo "$file2"
      s=$(echo "$file1" | sed "s/.*$date//;s/[_].*//")
      e=$(echo "$file2" | sed "s/.*$date[0-9]//;s/[_].*//")
      site=$site1$s"-"$e
      sed -i "/site/c\site=$site" config.test
      sed -i "/file1/c\file1=$file1" config.test
      sed -i "/file2/c\file2=$file2" config.test
      cat config.test
      bash $scr config.test 
      echo "$file2"
      echo "$file3"
      s=$(echo "$file2" | sed "s/.*$date//;s/[_].*//")
      e=$(echo "$file3" | sed "s/.*$date[0-9]//;s/[_].*//")
      site=$site1$s"-"$e
      sed -i "/site/c\site=$site" config.test
      sed -i "/file1/c\file1=$file2" config.test
      sed -i "/file2/c\file2=$file3" config.test
      cat config.test
      bash $scr config.test
      echo "$file3"
      echo "$file4"
      s=$(echo "$file3" | sed "s/.*$date//;s/[_].*//")
      e=$(echo "$file4" | sed "s/.*$date[0-9]//;s/[_].*//")
      site=$site1$s"-"$e
      sed -i "/site/c\site=$site" config.test
      sed -i "/file1/c\file1=$file3" config.test
      sed -i "/file2/c\file2=$file4" config.test
      cat config.test
      bash $scr config.test 
    fi
    if test $num -eq 6 ;then
      file2=${fileArray3[$i]}
      file3=${fileArray2[$i+1]}
      file4=${fileArray[$i+2]}
      echo "$file1"
      echo "$file2"
      s=$(echo "$file1" | sed "s/.*$date//;s/[_].*//")
      e=$(echo "$file2" | sed "s/.*$date[0-9]//;s/[_].*//")
      site=$site1$s"-"$e
      sed -i "/site/c\site=$site" config.test
      sed -i "/file1/c\file1=$file1" config.test
      sed -i "/file2/c\file2=$file2" config.test
      cat config.test
      bash $scr config.test 
      echo "$file2"
      echo "$file3"
      s=$(echo "$file2" | sed "s/.*$date//;s/[_].*//")
      e=$(echo "$file3" | sed "s/.*$date[0-9]//;s/[_].*//")
      site=$site1$s"-"$e
      sed -i "/site/c\site=$site" config.test
      sed -i "/file1/c\file1=$file2" config.test
      sed -i "/file2/c\file2=$file3" config.test
      cat config.test
      bash $scr config.test 
      echo "$file3"
      echo "$file4"
      s=$(echo "$file3" | sed "s/.*$date//;s/[_].*//")
      e=$(echo "$file4" | sed "s/.*$date[0-9]//;s/[_].*//")
      site=$site1$s"-"$e
      sed -i "/site/c\site=$site" config.test
      sed -i "/file1/c\file1=$file3" config.test
      sed -i "/file2/c\file2=$file4" config.test
      cat config.test
      bash $scr config.test 
      i=$((i+1))
    fi
    if test $num -eq 4 ;then
      file2=${fileArray[$((i+1))]}
      echo "$file1"
      echo "$file2"
      s=$(echo "$file1" | sed "s/.*$date//;s/[_].*//")
      e=$(echo "$file2" | sed "s/.*$date[0-9]//;s/[_].*//")
      site=$site1$s"-"$e
      sed -i "/site/c\site=$site" config.test
      sed -i "/file1/c\file1=$file1" config.test
      sed -i "/file2/c\file2=$file2" config.test
      cat config.test
      bash $scr config.test 
    fi
done
fi













