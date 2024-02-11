import os

import numpy as np

#Open the file with the list of the solving times for all solved LP files
f = open(os.getcwd()+"/TestData/probsoltime.txt", "r")
lines = f.readlines()
f.close()
times = []
for l in lines:
    times.append(float(l))

#Print the mean time, standard deviation, and maximum time
print("Mean: "+str(np.mean(times)))
print("Std Dev: "+str(np.std(times)))
print("Max: "+str(max(times)))
print("Total test time: "+str(sum(times)))

#Maximum number of consensus detected in one single problem
maxnum = 0
rootdir = os.getcwd()+"/TestData/LPs"
subdirs = []
for file in os.listdir(rootdir):
    d = os.path.join(rootdir, file)
    if os.path.isdir(d):
        subdirs.append(file)
for sub in subdirs:
    dict = {}
    for file in os.listdir(rootdir+"/"+sub):
        els = file.split("_")
        probnum = int(els[0].replace("Problem", "").replace("+", "").replace("-", ""))
        numcons = int(els[1].replace(".lp", ""))
        if probnum in dict.keys():
            dict[probnum] += numcons
        else:
            dict[probnum] = numcons
    for key in dict.keys():
        if dict[key] > maxnum:
            maxnum = dict[key]

print("Maximum number of consensus in a single problem: "+str(maxnum))

