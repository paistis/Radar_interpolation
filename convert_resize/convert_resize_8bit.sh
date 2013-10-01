#!/bin/bash
path=$PWD/convert_resize
EXPECTED_ARGS=2
E_BADARGS=65
#this scrpt convertss goetiff to png and resize it to next power of 2 for intrepolation
#check numeber of arguments
if [ $# -ne $EXPECTED_ARGS ]
then [ nan  nan  nan ...,  nan  nan  nan]

  echo "Usage: `basename $0` [raw filename] [sweep] [var] [scan name]"
  exit $E_BADARGS
fi
#convert geotiff to png 
gdal_translate -of PNG $1 $2
#check what is next power of 2
p2=`convert $2 -format "%[fx:2^(ceil(log(max(w,h))/log(2)))]" info:`
#scale image to next power of 2
convert $2 -background black -gravity center -extent ${p2}x${p2} $2
echo "re-size image"

