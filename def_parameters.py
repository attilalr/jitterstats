import sys, os
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
it=300
source='run.cpp'
laco=3

workt=sys.argv[1]
mean=sys.argv[2]
length=sys.argv[3]
nprocs=sys.argv[4]
output=sys.argv[5]

def test(source,workt,nprocs,ops,it,name):
  #compile first
  cmd='mpic++ '+source+' -DWORKTYPE='+str(workt)+' -DOPS_PER_ITERATION='+str(ops)+' -DITERATIONS='+str(it)+' -larmadillo -o '+name
  #print "Compiling..."
  #print cmd
  os.system(cmd)
  #executing
  #print "Executing..."
  cmd='mpirun -np '+str(nprocs)+' '+name
  if (workt==3):
    cmd='export OMP_NUM_THREADS=1 && export OPENBLAS_NUM_THREADS=1 && '+cmd
  #print cmd
  #print len(os.popen(cmd).read().split())
  result=np.array([float (x) for x in os.popen(cmd).read().split() if '#' not in x])
  #print result
  #print "Len result: "+str(len(result))
  os.system('rm '+name)
  return result.mean()

for i in range(laco):
  res=test(source,workt,nprocs,ops,it,'teste-run')
  ops=int(float(ops)*(0.001*float(mean))/res) # 0.001 is for msec. to sec.
  print "EL. TIME PER ITERATION: "+str(res)+" s. DESIRED TIME: "+str(float(mean)*0.001)+" s."

  #print "It: "+str(i)
  #print "OPS_PER_ITERATION: "+str(ops)

print "##########################################"
print "FINAL OPS AND IT PARAMETERS:"
print "OPS_PER_ITERATION: "+str(ops)
print "ITERATIONS for "+length+" minutes: "+str(int((int(length)*60.0/res)))
print "EL. TIME PER ITERATION: "+str(res)
print "NUMBER OF DATA: "+str(int(nprocs)*int((int(length)*60.0/res)))
print "##########################################"
print
#print "Run the command:"
#print 'export OMP_NUM_THREADS=1 && export OPENBLAS_NUM_THREADS=1 && '+"mpic++ run.cpp -larmadillo -DITERATIONS="+str(int((int(length)*60.0/res)))+" -DOPS_PER_ITERATION="+str(ops)+" -D WORKTYPE="+str(workt)+" -o outfile"
#print "mpirun -np "+str(nprocs)+" outfile"
cmd='export OMP_NUM_THREADS=1 && export OPENBLAS_NUM_THREADS=1 && '+"mpic++ run.cpp -larmadillo -DITERATIONS="+str(int((int(length)*60.0/res)))+" -DOPS_PER_ITERATION="+str(ops)+" -D WORKTYPE="+str(workt)+" -o outfile && mpirun -np "+str(nprocs)+" outfile > "+output
print "Running the command: "+cmd
print
os.system(cmd)