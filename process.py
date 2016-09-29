import numpy as np
import random
import sys
import matplotlib.pyplot as p
from multiprocessing import Pool


if len(sys.argv)!=2:
  print """
  Usage:
    python process.py datafile
  """
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

nsamples=200000
#for N in range(10,100,10):
  #I can change with the next line but I got no performance improvements
  #teste=map(lambda x:np.random.choice(nbins,size=N,p=np.array(datahist)*size_bin).max(),[0]*nsamples)
#  teste=list()
#  teste_gauss=list()
#  for i in range(nsamples):
#    teste.append(np.random.choice(nbins,size=N,p=np.array(datahist)*size_bin).max())
#    teste_gauss.append((results[0][2]*np.random.randn(N)+results[0][1]).max())
#  teste=np.array(teste)
#  teste_gauss=np.array(teste_gauss)
#  results.append([N,teste.mean(),teste.std(),teste_gauss.mean(),teste_gauss.std()])

def simulate((N,nsamples,datahist,nbins,size_bin,mean,std)):
  teste=list()
  teste_gauss=list()
  for i in range(nsamples):
    teste.append(np.random.choice(nbins,size=N,p=np.array(datahist)*size_bin).max())
    teste_gauss.append((std*np.random.randn(N)+mean).max())
  teste=np.array(teste)
  teste_gauss=np.array(teste_gauss)

  return [N,teste.mean(),teste.std(),teste_gauss.mean(),teste_gauss.std()]

#creating the entry parameters
N_list=[x for x in range(10,50000,2000)]
parameters=list()
for n in N_list:
  parameters.append((n,nsamples,datahist,nbins,size_bin,mean,std))
pool=Pool(processes=len(N_list))
results=pool.map(simulate,parameters)

#print mean, std
#for i in results:
#  print i
#  datahist_tmp,bins_tmp = np.histogram(teste,bins=100,density=True)
#  color=random.choice(['r','g','b','y'])
#  p.plot(bins_tmp[:-1,],datahist_tmp,color+'o--')
#p.show()

print "# "+str(mean)+" "+str(std)
print "# N slowdown sigma slowdon_gaussian sigma-slowdown_gaussian"
for res in results:
  print res[0], ((res[1]-mean)/mean)*100, ((res[1]+res[2]-mean)/mean)*100-((res[1]-mean)/mean)*100, ((res[3]-mean)/mean)*100, ((res[3]+res[4]-mean)/mean)*100-((res[3]-mean)/mean)*100

file.close()
