# include <cstdlib>
# include <iostream>
# include <iomanip>
# include <ctime>

#include<armadillo>
using namespace arma;

using namespace std;

# include "mpi.h"

// define WORKTYPE (1 or 2) and OPS_PER_ITERATION (10000000)
// define ITERATIONS 10000 lenght of test
#ifndef WORKTYPE
#define WORKTYPE 1
#endif

#ifndef OPS_PER_ITERATION
#define OPS_PER_ITERATION 100000000
#endif

#ifndef ITERATIONS
#define ITERATIONS 20000
#endif

//****************************************************************************

int main ( int argc, char *argv[] ) {

  int id;
  int p;
  char name[MPI_MAX_PROCESSOR_NAME];
  int len;

  int s=0, i, j;

  std::clock_t start;
  double duration;

  double x=0,y=0, res=0;

  MPI::Init(argc,argv);

  p = MPI::COMM_WORLD.Get_size ( );
  id = MPI::COMM_WORLD.Get_rank ( );

  memset(name,0,MPI_MAX_PROCESSOR_NAME);
  MPI::Get_processor_name(name,len);
  memset(name+len,0,MPI_MAX_PROCESSOR_NAME-len);

  // defining a vector
  // size (kB)= VSIZE * 8 / 1024 
  
  if (WORKTYPE==1) {
      int VSIZE=98304;
      int a[VSIZE];
      for (i=0;i<VSIZE;i++)
        a[i]=i;

      /* work type 1*/  
      for (j=0;j<ITERATIONS;j++) {
        MPI::COMM_WORLD.Barrier();
        start = std::clock();
        for (i=0;i<OPS_PER_ITERATION;i++) {
          s = s+(a[i%VSIZE])^s;
        }
        duration = ( std::clock() - start ) / (double) CLOCKS_PER_SEC;
        std::cout << (double)duration << std::endl;
      }
  }

  if (WORKTYPE==2) {
      srand(time(0)+(int)p*(int)id);
      /* work type 1, static monte carlo*/  
      for (j=0;j<ITERATIONS;j++) {
        MPI::COMM_WORLD.Barrier();
        start = std::clock();
        s=0;
        for (i=0;i<OPS_PER_ITERATION;i++); {
          x=(1.0*rand())/(1.0+RAND_MAX);
          y=(1.0*rand())/(1.0+RAND_MAX);
          if (x*x + y*y < 1)
            s++;
        }
        res=1.0*s/OPS_PER_ITERATION;
        duration = ( std::clock() - start ) / (double) CLOCKS_PER_SEC;
        std::cout << (double)duration << std::endl;
      }
  }

  if (WORKTYPE==3) {
      int size=100;
      /* work type 3*/  
      for (j=0;j<ITERATIONS;j++) {
        MPI::COMM_WORLD.Barrier();

        start = std::clock();
        for (i=0;i<OPS_PER_ITERATION;i++); {
          mat A = randu(size,size);
          mat B = randu(size,size);
          mat Z = zeros(size,size);

          Z=A*B;
        }

        duration = ( std::clock() - start ) / (double) CLOCKS_PER_SEC;
        std::cout << (double)duration << std::endl;
      }
  }

  MPI::Finalize();

  return 0;
}
//****************************************************************************


