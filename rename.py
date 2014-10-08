import sys, os
import pyart
import geotiff2png

# MAIN
try:
  FILENAME = sys.argv[1]
except:
  print "usage run_RENAMING.py [init file]"
  os._exit(o)

geotiff2png.rename_file(FILENAME)
