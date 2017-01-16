import numpy as np
import random, math
import sys, time
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
  if (line.find("#")==-1 and line!='\n'):
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

am_work=5000000
nsamples=300000

def simulate((am_work,calc_gauss,N,nsamples,datahist,nbins,size_bin,mean,std)):
  teste=list()
  sum_tmax=0
  idleness=0
  idleness2=0
  comp_time=0
  comp_time2=0

  f=(1.0*am_work)/N/nsamples # corr factor , (Am_work/N) / nsamples , theoretical iterations / effective iterations
  
  for i in xrange(nsamples):
    if calc_gauss==0: # use profile distribution
      sample_list=np.random.choice(nbins,size=N,p=np.array(datahist)*size_bin)
    if calc_gauss==1: # use normal distribution with mean and std based on profile
      sample_list=std*np.random.randn(N)+mean

    tmax=sample_list.max()
 
    sum_tmax=sum_tmax+tmax # sum tmax, effective computing time
    idleness=idleness+(N*tmax-sample_list.sum())/(N*tmax)
    idleness2=idleness2+(N*tmax-sample_list.sum())/(N*tmax)*(N*tmax-sample_list.sum())/(N*tmax)
    comp_time=comp_time+sample_list.sum()/(N*tmax)
    comp_time2=comp_time2+sample_list.sum()/(N*tmax)*sample_list.sum()/(N*tmax)
    
    teste.append(tmax)
    
  mean_idleness=idleness/nsamples
  mean_eff_comp=comp_time/nsamples
  
  s_idleness=math.sqrt(idleness2/nsamples-mean_idleness*mean_idleness)
  s_eff_comp=math.sqrt(comp_time2/nsamples-mean_eff_comp*mean_eff_comp)
  
  teste=np.array(teste)

#  return [N,teste.mean(),teste.std(),sum_tmax/f,nsamples*teste.std(),mean_idleness,s_idleness,mean_eff_comp,s_eff_comp]
  return [N,teste.mean(),teste.std(),sum_tmax*f,(float(N)/am_work)*teste.std(),mean_idleness,(float(N)/am_work)*s_idleness,mean_eff_comp,(float(N)/am_work)*s_eff_comp]

# simulate_light calculate just the elapsed time
#def simulate_light((am_work,calc_gauss,N,nsamples,datahist,nbins,size_bin,mean,std)):
#  sum_tmax=0
#  f=(1.0*am_work)/N/nsamples # (Am_work/N) / nsamples , theoretical iterations / effective iterations
  
#  for i in xrange(nsamples):
#    if calc_gauss==0: # use profile distribution
#      sample_list=np.random.choice(nbins,size=N,p=np.array(datahist)*size_bin)
#    if calc_gauss==1: # use normal distribution with mean and std based on profile
#      sample_list=std*np.random.randn(N)+mean

#    tmax=sample_list.max()
 
#    sum_tmax=sum_tmax+tmax # sum tmax, effective computing time

#  return [N,0,0,sum_tmax*f,0,0,0,0,0]


#creating the entry parameters
# put 1 to calibrate
#N_list=[x for x in range(10,100,10)]+[x for x in range(100,1000,100)]+[x for x in range(1000,10000,1000)]
#N_list=[x for x in range(10,400,20)]+[x for x in range(400,20000,100)]
N_list=[1]+[x for x in range(1000,20000,2000)]+[x for x in range(20000,200000,5000)]

# acessory list with N+1
#N_list_next=(np.array(N_list)+1).tolist()

#
t=time.time()
parameters=list()
for n in N_list:
#  nsamples=int(am_work/n) # ideal parallelization
  parameters.append((am_work,calculate_gaussian,n,nsamples,datahist,nbins,size_bin,mean,std))
pool=Pool(processes=len(N_list))
results=pool.map(simulate,parameters)
print "#"+str(time.time()-t)+" seconds to run the main data."

# list with N's +1
#t=time.time()
#parameters=list()
#for n in N_list_next:
#  nsamples=int(am_work/n) # ideal parallelization, look here for dispersion because of int()
#  parameters.append((am_work,calculate_gaussian,n,nsamples,datahist,nbins,size_bin,mean,std))
#pool=Pool(processes=len(N_list_next))
#results_n=pool.map(simulate_light,parameters)
#print "#"+str(time.time()-t)+" seconds to run the aux data."

t0=results[0][3]
n0=results[0][0]

print "# "+str(mean)+" "+str(std)
print "# N | slowdown | sigma | t_eff_finish | s_t_eff_finish | ideal_t_eff_finish | t_eff_diff_from_ideal | t_eff_diff_from_ideal(relative) | mean idleness | s_mean_idl | mean effective computing | s_mean_eff_comp"

#for res,res_n in zip(results,results_n):
for res in results:
  if (res[0]!=1):
    print res[0], ((res[1]-mean)/mean)*100, ((res[1]+res[2]-mean)/mean)*100-((res[1]-mean)/mean)*100,res[3]/t0, res[4]/t0, (t0*n0)/(res[0]*t0), res[3]-(t0*n0)/res[0], (res[3]-(t0*n0)/res[0])/((t0*n0)/res[0]) ,res[5], res[6], res[7], res[8]
  
