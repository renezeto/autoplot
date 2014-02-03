from __future__ import division
import numpy as np

datasets = ["data2.CSV","data3.CSV","data4.CSV"]
N = .04 #from fresnel at theta=0

for filename in datasets:
    loaded_data = np.loadtxt(filename)
    if filename == "data2.CSV":
        N = .04
    if filename == "data3.CSV":
        N = 1 - .04
    if filename == "data4.CSV":
        N = 1 - .04
    for i in loaded_data:
        i[1] = N*i[1]
    with open(filename,"w") as datafile:
        for i in loaded_data:
            datafile.write("%f %f\n"%(i[0], i[1]))

print "done"
