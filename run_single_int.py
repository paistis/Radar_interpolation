import interpolation
RADAR_FILE1_path="/home/Radar/data/RAW/VAN/2010-08-08/201008081800_VAN.PPI1_A.raw"
RADAR_FILE2_path="/home/Radar/data/RAW/VAN/2010-08-08/201008081810_VAN.PPI3_A.raw"
timestep=11
#images='images/'
#morh='morph/'
filename='VAN10008081800-1810'
output='/home/Radar/Int_Data/'


#interpolation.interpolate(RADAR_FILE1_path,RADAR_FILE2_path,timestep,images,morh,filename,0,['DBZ2','HCLASS2','KDP2','VEL2','RHOHV2'],output)
interpolation.interpolate(RADAR_FILE1_path,RADAR_FILE2_path,timestep,filename,0,['DBZ2','HCLASS2','KDP2','VEL2','RHOHV2'],output)

