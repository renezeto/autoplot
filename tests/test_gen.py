#!/usr/bin/env python
from __future__ import division

print "***********************************************************************"
print "autoplot.py must be in PYTHONPATH, run with:"
print "\"PYTHONPATH=/path/to/autoplot ./test_gen.py\" or move autoplot to a"
print "directory in PYTHONPATH, otherwise this program will fail to run"
print "***********************************************************************"

import numpy as np
import glob
import os
import sys
import random
import autoplot

if "-clean" in sys.argv:
    print "Deleting existing dataset_n tests."
    os.system("rm -rf dataset_*")
    print "Done."
    exit(0)

elif len(sys.argv)<2:
    print "Tell me how many tests you want! Or invoke the -clean command to remove old tests."
    exit(1)
else:
    num_tests = int(sys.argv[1])

test_counter = 0

num_existing_tests=0
for file in glob.iglob("dataset_*"):
    num_existing_tests += 1

def square_wave(t,m):
    f = np.zeros_like(t,dtype="float")
    for n in [k for k in range(1,m+1) if (-1)**k==-1]:
        a_n = (2/(n*np.pi))*(1 - (-1)**n)
        f += a_n*np.sin(n*np.pi*t)
    return f
    
dt = 1/512
t = np.arange(0,2,dt)
for i in range(num_existing_tests,num_tests+num_existing_tests):
    path = "dataset_%d"%(i+num_existing_tests)
    os.makedirs(path)
    m = random.randint(0,10000)
    f = square_wave(t,m)
    with open("%s/test_data_%d.CSV"%(path,m),"w+") as data_file:
        for i in range(len(f)):
            data_file.write("%f %f\n"%(t[i], f[i]))
    with open("%s/autoplotlist.txt"%path,"w+") as autoplot_file:
        autoplot_file.write("data=\"test_data_%d.CSV\" title=\"Fourier expansion of a square wave, first %d terms.\" xlabel=\"t\" ylabel=\"f_%d(t)\""%(m,m,m))
    old_pwd = os.getcwd()
    os.chdir(path)
    aplot = autoplot.Autoplot("autoplotlist.txt")
    aplot.processJobs()
    os.chdir(old_pwd)
