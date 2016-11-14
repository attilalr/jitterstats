# jitterstats
Collection of routines to profile jitter in you computer and estimate the slowdown when scaling to arbitrary number of processes.

Dependencies:
mpi
armadillo lib
numpy

```
  Usage:
    python def_parameters.py WORKTYPE mean(ms) length(min) nprocs output.dat
    
    WORKTYPE: 1 | 2 | 3
    mean: the program will find the parameters to make each run consume mean milisseconds aprox.
    lenght: total time of the runs
    nprocs: number of cores to use, usually is the real cores number
    output.dat: data time series to use with process.py
```
