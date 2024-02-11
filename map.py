import os
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np

#THIS CODE GENERATES THE MAP PLOT WITH VARYING GENERALISATION RELATION AND KNOWN PREFERENCE PERCENTAGES

#We get all the data from the testdata file
lines = {}
f = open(os.getcwd()+"/TestData/testdata.txt", "r")
filelines = f.readlines()
l = filelines[0]
gen = int(l.split("N")[1].split("G")[0])
lastgen = gen
pref = int(l.split("N")[1].split("G")[1].replace("P",""))
dataarray = []
times = []
timesgen = []
for l in filelines[1:]:
    if "TEST" in l:
        gen = int(l.split("N")[1].split("G")[0])
        pref = int(l.split("N")[1].split("G")[1].replace("P", ""))
        timesgen.append(np.mean(times))
        times = []
        if gen > lastgen:
            lastgen = gen
            dataarray.append(timesgen)
            timesgen = []
    if "Problem" in l:
        times.append(float(l.replace(" ", "").split(":")[1].split("(")[0]))
timesgen.append(np.mean(times))
dataarray.append(timesgen)
data = np.array(dataarray[::-1])

#We make the plot and save it
fig, ax = plt.subplots()
im = ax.imshow(data, cmap = "rainbow", norm = colors.LogNorm(), extent=[0,100,0,100])
cbar = plt.colorbar(im)
cbar.set_label('Seconds')
plt.xlabel('Percentage of known preferences')
plt.ylabel('Generalisation relation percentage')
plt.axis('tight')
plt.savefig(os.getcwd()+"/ConfigTimes.pdf", bbox_inches='tight')