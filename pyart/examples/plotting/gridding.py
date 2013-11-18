import pyart

filename = '201008081805_VAN.PPI2_A.raw'
radar = pyart.io.read_sigmet(filename,sigmet_field_names=True, time_ordered='none')
dist = radar.range['data'][-1]
rcells = radar.ngates

grid = pyart.map.grid_from_radars(
    (radar,),
    grid_shape=(rcells*2, rcells*2, 5),
    grid_limits=((dist, -dist), (dist, -dist),
                 (10, 10)),
    fields=['DBZ2','HCLASS2'])
grid.write("hclass_grid1.nfc")
print "saving grid one"
grid.write("/home/nordlikg/Documents/pyart-master/pyart/examples/plotting/hclass_test.tiff",'GTiff')
