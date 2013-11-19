import interpolation
import sys,os,glob

#read config file
#config = sys.argv[1]
#execfile(config)

time_intervals = [5,10,15]
start_time=1800
end_time=1900
site="VAN"
data_path = "/home/nordlikg/Documents/data/RAW/VAN/2010-08-08/"
date=20100808

try:
	os.mkdir(site)
except:
	print "Site folder already exist.. not creating it"
try:
	os.mkdir(site+"/"+str(date))
except:
	print "Site folder already exist.. not creating it"

for step in time_intervals:
	for i in range(0,step):

		timesteps=step+1
		start=start_time+i
		end=start+step
		RADAR_FILE1=data_path+glob.glob(str(date)+str(start)+"_VAN.PPI*_A.raw")[0]
		RADAR_FILE2=data_path+glob.glob(str(date)+str(end)+"_VAN.PPI*_A.raw")[0]

		name=str(start)+"-"+str(end)
		try:
			os.mkdir(site+"/"+str(date)+"/"+name)
		except:
			print "Site name folder already exist"
		try:
			os.mkdir(site+"/"+str(date)+"/"+name+"/image/")
		except:
			print "Site image folder already exist"
		try:
			os.mkdir(site+"/"+str(date)+"/"+name+"/morph/")
		except:
			print "Site morph folder already exist"

		
		images=site+"/"+str(date)+"/"+name+"/image/"
		morp=site+"/"+str(date)+"/"+name+"/morph/"
		filename=str(date)+"_"+site+"_"+name	
	
		interpolation.interpolate(RADAR_FILE1,RADAR_FILE2,timesteps,images,morp,filename)

		#write log
		fo=open((site+"/"+str(date)+"/"+name+"/"+name+".log"),"w+")
		fo.write("site: "+site+"\n")
		fo.write("timestep: "+str(timesteps)+"\n")
		fo.write("name: "+name+"\n")
		fo.write("RADAR_FILE1: "+RADAR_FILE1)
		fo.write("RADAR_FILE2: "+RADAR_FILE2)
		fo.write("filename: "+filename)

		
