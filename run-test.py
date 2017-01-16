import sys, os, time
import numpy as np

# parametros de entrada: WORKTYPE mean length nprocs output

#values to set:
#define WORKTYPE 1
#define OPS_PER_ITERATION 10000000
#define ITERATIONS 10000

if (len(sys.argv)!=(5+1) and len(sys.argv)!=(6+1) and len(sys.argv)!=(7+1)):
  print """
  Usage:
    python run-test.py WORKTYPE mean(ms) length(min) nprocs [--excl-0] [--set-it-ops=n,m] output.dat
    
    WORKTYPE: 1 | 2 | 3
    mean: the program will find the parameters to make each run consume mean milisseconds aprox.
    lenght: total time of the runs
    nprocs: number of cores to use, usually is the real cores number
    output.dat: data time series to use with process.py
    --excl-0: option to exclude cpu 0 from computing for tickless cases where cpu 0 maintains its ticks,
              it will pinne the nprocs processes in each other cores.
    --set-it-ops=n,m: if you want to set manually ITERATIONS and OPS, it will ignore mean and lenght
  """
  print len(sys.argv)
  sys.exit(0)

ops=10000
it=4000
source='run.cpp'
laco=20
skip_per_proc=400

workt=sys.argv[1]
mean=sys.argv[2]
length=sys.argv[3]
nprocs=sys.argv[4]
output=sys.argv[-1]

it=it+skip_per_proc*int(nprocs)

# exclude cpu 0 option
if ('--excl-0' in sys.argv):
  exclude_cpu_0=1
  #now create the rank.lst file
  string=''
  for i in range(int(nprocs)):
    string=string+"rank "+str(i)+"=localhost slot="+str(i+1)+"\n"
  file=open('rank.lst','w')
  file.write(string)
  file.close()
else:
  exclude_cpu_0=0
  
# treat set IT and OPS manually
it_ops_manual=0
for p in sys.argv:
  #--set-it-ops=n,m
  if '--set-it-ops=' in p:
    it_ops_manual=1
    try:
      it=int(p.split('=')[1].split(',')[0])
      ops=int(p.split('=')[1].split(',')[1])
      print "it,ops: "+str(it)+' '+str(ops)
    except:
      print " Error in --set-it-ops parameter."
      sys.exit(0)

def test(source,workt,nprocs,ops,it,name,exclude_cpu_0,skip_per_proc):
  #compile first
  cmd='mpic++ '+source+' -DWORKTYPE='+str(workt)+' -DOPS_PER_ITERATION='+str(ops)+' -DITERATIONS='+str(it)+' '+(lambda x: ' -DARMADILLO=1 -larmadillo' if x=='3' else '')(workt)+' -o '+name
  print cmd
  #executing
  os.system(cmd)
  cmd='mpirun -np '+str(nprocs)+' '+(lambda x: '-H localhost -rf rank.lst' if x==1 else '')(exclude_cpu_0)+' '+name
  if (workt==3):
    cmd='export OMP_NUM_THREADS=1 && export OPENBLAS_NUM_THREADS=1 && '+cmd
  print cmd 
  result=np.array([float (x) for x in os.popen(cmd).read().split() if '#' not in x])
  #print os.system('rm '+name)
  print len(result)
  return result[(skip_per_proc*int(nprocs)):].mean()
    


if (it_ops_manual==0):
  for i in range(laco):
    res=test(source,workt,nprocs,ops,it,'teste-run',exclude_cpu_0,skip_per_proc)
    print "EL. TIME PER ITERATION: "+str(res)+" s. DESIRED TIME: "+str(float(mean)*0.001)+" s."
    ops=int(float(ops)*0.001*float(mean)/res) # 0.001 is for msec. to sec.
  #  print 'abs('+str(res)+' - '+' '+str(0.001*float(mean))+')'
  #  print "dif: "+str(abs(res-(0.001*float(mean))))
    if (abs(res-(0.001*float(mean)))<0.0002):
      break
    if (i==range(laco)[-1]):
      print " Could not set OPS parameters correctly. Change ops in this source code."
      sys.exit(0) 

print "##########################################"
print "FINAL OPS AND IT PARAMETERS:"
print "OPS_PER_ITERATION: "+str(ops)
if (it_ops_manual==0):
  print "ITERATIONS for "+length+" minutes (per core): "+str(int(((int(length)*60.0)/(res*int(1)))))
  print "EL. TIME PER ITERATION: "+str(res)
  print "NUMBER OF DATA IN TIME SERIES: "+str(int(nprocs)*int((int(length)*60.0/res)))
else:
  print "ITERATIONS: "+str(it)
print "##########################################"
print

if (it_ops_manual==0):
  cmd='export OMP_NUM_THREADS=1 && export OPENBLAS_NUM_THREADS=1 && '+"mpic++ run.cpp "+(lambda x: '-DARMADILLO=1 -larmadillo' if x=='3' else '')(workt)+" -DITERATIONS="+str(int(((int(length)*60.0)/(res*int(1)))))+" -DOPS_PER_ITERATION="+str(ops)+" -D WORKTYPE="+str(workt)+" -o outfile && mpirun -np "+str(nprocs)+' '+(lambda x: '-H localhost -rf rank.lst' if x==1 else '')(exclude_cpu_0)+" outfile"
else:
  cmd='export OMP_NUM_THREADS=1 && export OPENBLAS_NUM_THREADS=1 && '+"mpic++ run.cpp "+(lambda x: '-DARMADILLO=1 -larmadillo' if x=='3' else '')(workt)+" -DITERATIONS="+str(it)+" -DOPS_PER_ITERATION="+str(ops)+" -D WORKTYPE="+str(workt)+" -o outfile && mpirun -np "+str(nprocs)+' '+(lambda x: '-H localhost -rf rank.lst' if x==1 else '')(exclude_cpu_0)+" outfile"

print "Running the command: "+cmd
print
data_ts=os.popen(cmd).read()
t=time.time()
print " Finished in "+str(float(time.time()-t)/60.0)+" minutes"
print " Writing data to file "+output
print

try:
  file=open(output,'w')
  file.write('#'+os.popen('uname -a').read())
  file.write('#it '+str(it)+' ops: '+str(ops)+'\n')
  file.write(data_ts)
  file.close()
except:
  print " Error writing data." 

