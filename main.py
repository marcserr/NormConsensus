from NormConsensusTest import *
import os
import shutil
import random

#We initialise the seed for the reproducibility of the random generation of the experiments
SEED = 2023
random.seed(SEED)

def main():

    #These are the parameters of the experiment
    NUM_TESTS = 10
    NUM_NODES = 100
    NUM_USERS = 5
    REL_PER = [x/100 for x in range(0,101,5)]
    PREF_PROB = [x/100 for x in range(5,101,5)]
    APP_PROB = 0.5

    #The paths of the result files
    DATA_FILE = os.getcwd()+"/TestData/testdata.txt"
    TIME_FILE = os.getcwd() + "/TestData/probsoltime.txt"

    #We ensure the TestData directory exists
    testdatadir = os.getcwd() + "/TestData/"
    if not os.path.exists(testdatadir):
        os.makedirs(testdatadir)

    #We ensure the directries to save the LP and solution files exist and save their paths
    lpdir = os.getcwd() + "/TestData/LPs/"
    if not os.path.exists(lpdir):
        os.makedirs(lpdir)
    soldir = os.getcwd() + "/TestData/SOLs/"
    if not os.path.exists(soldir):
        os.makedirs(soldir)

    #We remove any files in the LP directory
    for remfilename in os.listdir(lpdir):
        if os.path.isfile(lpdir + remfilename) or os.path.islink(lpdir + remfilename):
            os.remove(lpdir + remfilename)
        elif os.path.isdir(lpdir + remfilename):
            shutil.rmtree(lpdir + remfilename)

    #We remove any files in the SOL directory
    for remfilename in os.listdir(soldir):
        if os.path.isfile(soldir + remfilename) or os.path.islink(soldir + remfilename):
            os.remove(soldir + remfilename)
        elif os.path.isdir(soldir + remfilename):
            shutil.rmtree(soldir + remfilename)

    #We open the ouutput files
    outfile = open(DATA_FILE, "w")
    normtimefile = open(TIME_FILE, "w")

    #For each configuration of relation percentage and preference probability we do the following
    for rel_per in REL_PER:
        for pref_prob in PREF_PROB:

            #We create new directories for this specific experiment configuration where we will save the lp and sol files
            lpdir = os.getcwd() + "/TestData/LPs/"+str(NUM_USERS)+"U"+str(NUM_NODES)+"N"+str(int(rel_per*100))+"G"+str(int(pref_prob*100))+"P/"
            soldir = os.getcwd() + "/TestData/SOLs/"+str(NUM_USERS)+"U"+str(NUM_NODES)+"N"+str(int(rel_per*100))+"G"+str(int(pref_prob*100))+"P/"
            if not os.path.exists(lpdir):
                os.makedirs(lpdir)
            if not os.path.exists(soldir):
                os.makedirs(soldir)

            #We run the test with this configuration and print the time it took to solve all problems generated
            print("TEST"+str(NUM_USERS)+"U"+str(NUM_NODES)+"N"+str(int(rel_per*100))+"G"+str(int(pref_prob*100))+"P")
            outfile.write("TEST"+str(NUM_USERS)+"U"+str(NUM_NODES)+"N"+str(int(rel_per*100))+"G"+str(int(pref_prob*100))+"P\n")
            test = NormConsensusTest(NUM_TESTS, NUM_NODES, rel_per, NUM_USERS, pref_prob, APP_PROB,lpdir,soldir,outfile,normtimefile)
            final_time = test.runfulltest()
            print("OVERALL TIME: "+str(final_time))
            outfile.write("OVERALL TIME: "+str(final_time)+"\n")

main()