import numpy as np
import random
import sys
from multiprocessing import Pool

calculate_gaussian=0

if (len(sys.argv)!=2 and len(sys.argv)!=3):
  print """
  Usage:
    python process.py datafile [--gauss=1] > results.dat
  """
  sys.exit(0)

if (len(sys.argv)==3 and sys.argv[2]=='--gauss=1'):
  calculate_gaussian=1 
  
if (len(sys.argv)==3 and sys.argv[2]!='--gauss=1'):
  print " Unrecognized option "+sys.argv[2]
  sys.exit(0)

datafile=sys.argv[1]
data_array=list()

try:
  file=open(datafile,'r')
except:
  print " Problem opening datafile."
  sys.exit(0)

line=file.readline()
while(line):
  if line.find("#") == -1:
    data_array.append(float(line.split()[0]))
  line=file.readline()

if (len(data_array)==0):
  print " Datafile empty, exiting..."
  sys.exit(0)

np_data=np.array(data_array)

results=list()
print "# Size of data: "+str(len(data_array))
print "# Mean: "+str(np_data.mean()) 
print "# std. dev.: "+str(np_data.std()) 
mean=np_data.mean()
std=np_data.std()

datahist,bins = np.histogram(np_data,bins=400,density=True)

# nbins is centralized bins
nbins=list()
size_bin=bins[1]-bins[0] # considerring all the bins with same width
for i in range(1,len(bins)):
  nbins.append((bins[i]+bins[i-1])/2)

am_work=20000000
#nsamples=200000

def simulate((calc_gauss,N,nsamples,datahist,nbins,size_bin,mean,std)):
  teste=list()
  sum_tmax=0
  idleness=0
  comp_time=0
  
  for i in range(nsamples):
    if calc_gauss==0: # use profile distribution
      sample_list=np.random.choice(nbins,size=N,p=np.array(datahist)*size_bin)
    if calc_gauss==1: # use normal distribution with mean and std based on profile
      sample_list=std*np.random.randn(N)+mean

    tmax=sample_list.max()
 
    sum_tmax=sum_tmax+tmax # sum tmax, effective computing time
    idleness=idleness+(N*tmax-sample_list.sum())/(N*tmax)
    comp_time=comp_time+sample_list.sum()/(N*tmax)
    
    teste.append(tmax)
    
  mean_idleness=idleness/nsamples
  mean_eff_comp=comp_time/nsamples
  
  teste=np.array(teste)

  return [N,teste.mean(),teste.std(),sum_tmax,mean_idleness,mean_eff_comp]

#creating the entry parameters
#N_list=[x for x in range(10,100,10)]+[x for x in range(100,1000,100)]+[x for x in range(1000,10000,1000)]
N_list=[x for x in range(1000,100000,1000)]
parameters=list()
for n in N_list:
  nsamples=int(am_work/n)
  parameters.append((calculate_gaussian,n,nsamples,datahist,nbins,size_bin,mean,std))
pool=Pool(processes=len(N_list))
results=pool.map(simulate,parameters)

t0=results[0][3]
n0=results[0][0]

print "# "+str(mean)+" "+str(std)
print "# N | slowdown | sigma | t_eff_finish | ideal_t_eff_finish | mean idleness | mean effective computing"
for res in results:
  print res[0], ((res[1]-mean)/mean)*100, ((res[1]+res[2]-mean)/mean)*100-((res[1]-mean)/mean)*100,res[3]/t0, (t0*n0)/(res[0]*t0), res[4], res[5]

file.close()
