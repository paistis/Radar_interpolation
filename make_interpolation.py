import interpolation
import sys,os,glob

#read config file
#config = sys.argv[1]
#execfile(config)

cases = {'2011-11-27':'1900-1500','2011-12-26':'0200-0300','2012-03-28':'1700-1800','2012-06-17':'0700-0800','2012-06-17':'1400-1500','2012-04-01':'1100-1300','2012-10-05':'1200-1300','2012-12-26':'1900-2000','2013-08-14':'1200-1300'}
sites = ['KUM','VAN','KER']
data_path = "/home/Radar/Int_Data/"
raws = "/home/Radar/data/"
#cases= {'2010-07-15':'1500-1600','2010-08-08':'1800-1900'}
for site in sites:
	print site
	for day, hours in cases.items():
		time_intervals = [5,10,15]
		start_time=hours.split('-')[0]
		end_time=hours.split('-')[1]
		date=''.join(day.split('-'))
		sweep=0


		for step in time_intervals:
			if (step == 5) and (site != 'VAN'):
				print step
				print "skipping"
				continue
			if (site == 'KER') and (step != 15):
				print step
				print "skipping"
				continue
			for i in range(0,60/step):

				timesteps=step+1
				start=int(start_time)+i*step
				end=int(start)+step
				if end >= int(start_time)+60:
					end=end_time
				
				print raws+"RAW/"+site+'/'+day+'/'+str(date)+str(start)+"*_"+site+"_ppi.raw"
				ERROR=''
				if site != 'VAN':
					try:
						RADAR_FILE1=glob.glob(raws+"RAW/"+site+'/'+day+'/'+str(date)+str(start)+"*_"+site+"_ppi.raw")[0]
						RADAR_FILE2=glob.glob(raws+"RAW/"+site+'/'+day+'/'+str(date)+str(end)+"*_"+site+"_ppi.raw")[0]
					except:
						continue
				else: 
					try:
						RADAR_FILE1=glob.glob(raws+"RAW/"+site+'/'+day+'/'+str(date)+str(start)+"_VAN.PPI*_A.raw")[0]
						RADAR_FILE2=glob.glob(raws+"RAW/"+site+'/'+day+'/'+str(date)+str(end)+"_VAN.PPI*_A.raw")[0]
					except:
						continue			
				name=str(start)+"-"+str(end)
		

				filename=site+"_"+date+'_'+'hours'+str(start)+'-'+str(end)+'_TS_'+str(step)
				fo=open(filename+".log","w")
				
				print "starting interpolation:"
				print "site: "+site
				print "timestep: "+str(timesteps)
				print "name: "+name
				print "Sweep: "+str(sweep)
				print "RADAR_FILE1: "+RADAR_FILE1
				print "RADAR_FILE2: "+RADAR_FILE2
				print "filename: "+filename

				interpolation.interpolate(RADAR_FILE1,RADAR_FILE2,timesteps,filename,sweep,['DBZ2','HCLASS2','KDP2','RHOHV2','VEL2'],data_path,fo)
				
				#write log
		
				fo.write("site: "+site+"\n")
				fo.write("timestep: "+str(timesteps)+"\n")
				fo.write("name: "+name+"\n")
				fo.write("Sweep: "+str(sweep)+"\n")
				fo.write("RADAR_FILE1: "+RADAR_FILE1+"\n")
				fo.write("RADAR_FILE2: "+RADAR_FILE2+"\n")
				fo.write("filename: "+filename)
				fo.close()
		
		
