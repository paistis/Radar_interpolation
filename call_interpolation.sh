#!/usr/bin/bash

# Data source directory
SRCD="/home/Radar/data/RAW/VAN/2010-07-15/"

# Directory where the interpolation script is located 
SCRD="/home/Radar/Radar_interpolation_lcr/Radar_interpolation/"

scr="run_single_int.py"

int=10
num=$((60/$int))
site1="VAN_20100715"
date="20100715"
timestep=$(($int+1))
flag_int=1

if test $flag_int -eq 1;then
 mask=*2010071515*PPI1_A*.raw
 mask2=*2010071515*PPI2_A*.raw
 mask3=*2010071515*PPI3_A*.raw
 mask4=*201007151600*PPI1_A*.raw
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
      site=$site1$s"-"$e"_TS_"$timestep
      python $scr  $file1 $file2 $timestep $site 
      echo "$file2"
      echo "$file3"
      s=$(echo "$file2" | sed "s/.*$date//;s/[_].*//")
      e=$(echo "$file3" | sed "s/.*$date[0-9]//;s/[_].*//")
      site=$site1$s"-"$e"_TS_"$timestep
      python $scr $file1 $file2 $timestep $site 
      echo "$file3"
      echo "$file4"
      s=$(echo "$file3" | sed "s/.*$date//;s/[_].*//")
      e=$(echo "$file4" | sed "s/.*$date[0-9]//;s/[_].*//")
      site=$site1$s"-"$e"_TS_"$timestep
      python $scr $file1 $file2 $timestep $site
    fi
    if test $num -eq 6 ;then
      file2=${fileArray3[$i]}
      file3=${fileArray2[$i+1]}
      file4=${fileArray[$i+2]}
      echo "$file1"
      echo "$file2"
      s=$(echo "$file1" | sed "s/.*$date//;s/[_].*//")
      e=$(echo "$file2" | sed "s/.*$date[0-9]//;s/[_].*//")
      site=$site1$s"-"$e"_TS_"$timestep
      python $scr $file1 $file2 $timestep $site
      echo "$file2"
      echo "$file3"
      s=$(echo "$file2" | sed "s/.*$date//;s/[_].*//")
      e=$(echo "$file3" | sed "s/.*$date[0-9]//;s/[_].*//")
      site=$site1$s"-"$e"_TS_"$timestep
      python $scr $file1 $file2 $timestep $site
      echo "$file3"
      echo "$file4"
      s=$(echo "$file3" | sed "s/.*$date//;s/[_].*//")
      e=$(echo "$file4" | sed "s/.*$date[0-9]//;s/[_].*//")
      site=$site1$s"-"$e
      python $scr $file1 $file2 $timestep $site 
      i=$((i+1))
    fi
    if test $num -eq 4 ;then
      file2=${fileArray[$((i+1))]}
      echo "$file1"
      echo "$file2"
      s=$(echo "$file1" | sed "s/.*$date//;s/[_].*//")
      e=$(echo "$file2" | sed "s/.*$date[0-9]//;s/[_].*//")
      site=$site1$s"-"$e"_TS_"$timestep
      python $scr $file1 $file2 $timestep $site
    fi
done
fi













