#!/usr/bin/env python

import argparse
from ipyparallel import Client
import numpy as np
import sympy
from helpers import stopwatch, to_numeric
import os


PI = 3.141592653589793

def worker_fun_1(n=1000):
  """ worker function """
  from random import random 
  s = 0
  for i in range(n):
    if random() ** 2 + random() ** 2 <= 1:
      s += 1
  
  return s 


def worker_fun_2(n=1000):
  """ worker function """
  import numpy as np

  chunksize = min(int(1e6), n)
 
  num_chunks, remainder = divmod(num_elems, chunksize)
  
  chunks = [chunksize] * num_chunks + ([remainder] if remainder else [])

  s = 0
  for chunk in chunks:
    s +=  int(
        np.sum(np.sum(np.square(np.random.rand(chunk, 2)), axis=1) <= 1.)
        )
  
  return s 


def main(profile, ntasks, niter, filename_out):
  rc = Client(profile=profile)
  views = rc[:]
  # with views.sync_imports():
  #  import numpy as np

  n = round(niter / ntasks)

  results = views.apply_sync(worker_fun_2, n)

  # Uses sypmy to compute the ratio to arbitrary precision
  my_pi = 4. * sympy.Rational(sum(results), (n * ntasks)).n(20)

  with open(filename_out, "w") as f:
    f.write("----------- Number of realizations: %0.0e -----------\n" % niter) 
    f.write("Estimate of pi: %0.16f\n" % my_pi)
    f.write("Actual pi:      %0.16f\n" % PI)
    f.write("Percent error:  %0.16f\n" % np.abs(100. * (PI - my_pi) / PI))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-p", "--profile", type=str, required=True,
      help="Name of IPython profile to use")
  parser.add_argument("-n", "--niter", type=str, required=True,
      help="Number of stochastic iterations")
  parser.add_argument("-o", "--output", type=str, required=True,
      help="Name of output file for writing")

  args = parser.parse_args()

  main(args.profile, 
      to_numeric(os.environ['SLURM_NTASKS']), 
      to_numeric(args.niter),
      args.output)

