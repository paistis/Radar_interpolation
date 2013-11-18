import pyart

filename = '201008081805_VAN.PPI2_A.raw'

# create the plot using RadarDisplay (recommended method)
radar = pyart.io.read_sigmet(filename,sigmet_field_names=True, time_ordered='none')
print radar.fields.keys()
