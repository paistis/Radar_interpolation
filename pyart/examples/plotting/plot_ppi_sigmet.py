"""
====================================
Create a PPI plot from a Sigmet file
====================================

An example which creates a PPI plot of a Sigmet file.

"""
print __doc__

# Author: Jonathan J. Helmus (jhelmus@anl.gov)
# License: BSD 3 clause

import matplotlib.pyplot as plt
import pyart

filename = '201008081805_VAN.PPI2_A.raw'

# create the plot using RadarDisplay (recommended method)
radar = pyart.io.read_sigmet(filename,sigmet_field_names=True, time_ordered='none')
display = pyart.graph.RadarDisplay(radar)

#print radar.fields.keys()
fig = plt.figure()
ax = fig.add_subplot(111)
#print display.fields
display.plot_ppi('HCLASS2', 0, vmin=-32, vmax=64.)
display.plot_range_rings([10, 20, 30, 40])
display.plot_cross_hair(5.)

plt.show()
