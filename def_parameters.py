import sys, os, time
import numpy as np

# parametros de entrada: WORKTYPE mean length nprocs output

#values to set:
#define WORKTYPE 1
#define OPS_PER_ITERATION 10000000
#define ITERATIONS 10000

if len(sys.argv)!=(5+1):
  print """
  Usage:
    python def_parameters.py WORKTYPE mean(ms) length(min) nprocs output.dat
    
    WORKTYPE: 1 | 2 | 3
    mean: the program will find the parameters to make each run consume mean milisseconds aprox.
    lenght: total time of the runs
    nprocs: number of cores to use, usually is the real cores number
    output.dat: data time series to use with process.py
  """
  print len(sys.argv)
  sys.exit(0)

ops=4000000
it=80
source='run.cpp'
laco=4

workt=sys.argv[1]
mean=sys.argv[2]
length=sys.argv[3]
nprocs=sys.argv[4]
output=sys.argv[5]

def test(source,workt,nprocs,ops,it,name):
  #compile first
  cmd='mpic++ '+source+' -DWORKTYPE='+str(workt)+' -DOPS_PER_ITERATION='+str(ops)+' -DITERATIONS='+str(it)+' '+(lambda x: ' -DARMADILLO=1 -larmadillo' if x==3 else '')(workt)+' -o '+name
  #executing
  os.system(cmd)
  cmd='mpirun -np '+str(nprocs)+' '+name
  if (workt==3):
    cmd='export OMP_NUM_THREADS=1 && export OPENBLAS_NUM_THREADS=1 && '+cmd
  result=np.array([float (x) for x in os.popen(cmd).read().split() if '#' not in x])
  os.system('rm '+name)
  return result.mean()

for i in range(laco):
  res=test(source,workt,nprocs,ops,it,'teste-run')
  ops=int(float(ops)*(0.001*float(mean))/res) # 0.001 is for msec. to sec.
  print "EL. TIME PER ITERATION: "+str(res)+" s. DESIRED TIME: "+str(float(mean)*0.001)+" s."

print "##########################################"
print "FINAL OPS AND IT PARAMETERS:"
print "OPS_PER_ITERATION: "+str(ops)
print "ITERATIONS for "+length+" minutes (per core): "+str(int(((int(length)*60.0)/(res*int(1)))))
print "EL. TIME PER ITERATION: "+str(res)
print "NUMBER OF DATA IN TIME SERIES: "+str(int(nprocs)*int((int(length)*60.0/res)))
print "##########################################"
print
cmd='export OMP_NUM_THREADS=1 && export OPENBLAS_NUM_THREADS=1 && '+"mpic++ run.cpp "+(lambda x: '-DARMADILLO=1 -larmadillo' if x==3 else '')(workt)+" -DITERATIONS="+str(int(((int(length)*60.0)/(res*int(1)))))+" -DOPS_PER_ITERATION="+str(ops)+" -D WORKTYPE="+str(workt)+" -o outfile && mpirun -np "+str(nprocs)+" outfile "
print "Running the command: "+cmd
print
data_ts=os.popen(cmd).read()
t=time.time()
print " Finished in "+str(float(time.time()-t)/60.0)+" minutes"
print " Writing data to file "+output
print

try:
  file=open(output,'w')
  file.write(data_ts)
  file.close()
except:
  print " Error writing data." 

