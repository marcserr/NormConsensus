from NormConsensusProblem import *
import time

class NormConsensusTest:
    """
    It represents a whole norm consensus test for one configuration of the problem. Therefore it generates and
    solves the required amount of norm consensus problems for that configuration
    """

    def __init__(self, numtests, numNodes, relPer, numUsers, prefProb, appProb, lpdir, soldir, outfile, normtimefile):
        # The number of nodes in the preference graphs
        self.numNodes = numNodes
        # The percentage of generalisation relations out of all possible in the graphs
        self.relPer = relPer
        # The number of users
        self.numUsers = numUsers
        #The probability of knowing the preference of a user to a node
        self.prefProb = prefProb
        # The probability of a known preference to be an approval one
        self.appProb = appProb
        # The number of total problems to generate and solve with the configuration above
        self.numtests  = numtests
        # The current problem number
        self.prob_num = 1
        # The current NormConsensusProblem
        self.problem = None
        # The directory of the LP files
        self.lpdir = lpdir
        # The directory of the solution files
        self.soldir = soldir
        # The file were we write the full results of the test
        self.outfile = outfile
        #The file were we write the solving times only
        self.normtimefile = normtimefile

    def runfulltest(self):
        """
        Runs the full test, that is generating and solving the required amount of NormConsensusProblem with the required
        configuration
        :return: The total time it took to solve the generated problems (in seconds)
        """

        #We initialise the total solving time to 0
        totaltesttime = 0

        #While we have not generates the required amount of problems
        while self.prob_num <= self.numtests:
            #We generate and solve one problem only and get the data and times for it
            probstatus, proptime, lptime, soltime = self.gensolveoneproblem()

            #We update the total solving time
            totaltime = proptime+lptime+soltime
            totaltesttime += totaltime

            #We print information about this problem in the console and in the file. Probstatus tells us wether there
            #were any positive (probstatus[0]) or negative (probstatus[1]) consensus
            if probstatus[0] and probstatus[1]:
                print("Problem"+str(self.prob_num-1)+"(+-):"+str(totaltime)+"("+str(proptime)+","+str(lptime)+","+str(soltime)+")")
                self.outfile.write("Problem"+str(self.prob_num-1)+"(+-):"+str(totaltime)+"("+str(proptime)+","+str(lptime)+","+str(soltime)+")\n")
            elif probstatus[0]:
                print("Problem"+str(self.prob_num-1)+"(+):"+str(totaltime)+"("+str(proptime)+","+str(lptime)+","+str(soltime)+")")
                self.outfile.write("Problem"+str(self.prob_num-1)+"(+):"+str(totaltime)+"("+str(proptime)+","+str(lptime)+","+str(soltime)+")\n")
            elif probstatus[1]:
                print("Problem"+str(self.prob_num-1)+"(-):"+str(totaltime)+"("+str(proptime)+","+str(lptime)+","+str(soltime)+")")
                self.outfile.write("Problem"+str(self.prob_num-1)+"(-):"+str(totaltime)+"("+str(proptime)+","+str(lptime)+","+str(soltime)+")\n")
            else:
                print("Problem"+str(self.prob_num-1)+"(ns):"+str(totaltime)+"("+str(proptime)+","+str(lptime)+","+str(soltime)+")")
                self.outfile.write("Problem"+str(self.prob_num-1)+"(ns):"+str(totaltime)+"("+str(proptime)+","+str(lptime)+","+str(soltime)+")\n")

        return totaltesttime

    def gensolveoneproblem(self):
        """
        We generate and solve one problem of the whole test
        :return: a list of two booleans containing whether we found positive and negative consensus respectively, and
        the times in seconds it took to propagate preferences, generate the first and any subsequent lp file, and
        solving the first and any subsequent LP files. All these times are part of the overall solving time of the
        problem.
        """

        #We generate the NormConsensusProblem with the required configuration
        self.problem = NormConsensusProblem(self.numNodes, self.relPer, self.numUsers, self.prefProb, self.appProb, self.prob_num, self.lpdir, self.soldir)
        proptime = self.problem.generateGraph()

        #We initialise the list and times
        problemsolvable = []
        soltime = 0

        #We solve the problem for both positive and negative consensuses
        for sign in [1, -1]:

            #We build the initial LP of the problem
            start_time = time.time()
            filename = self.problem.buildLp(sign)
            lp_time = time.time() - start_time

            #If we have built the LP we put True in the problemsolvable list, False otherwise
            if filename:
                lpbuilt = True
            else:
                lpbuilt = False
            problemsolvable.append(lpbuilt)

            #While there is an LP to solve
            while lpbuilt:
                #We solve one iteration of the problem and generate the next LP (containing the new solution
                #constraints)
                probsoltime, nextgentime = self.problem.solveone()
                #We update the solving and generation times
                lp_time += nextgentime
                soltime += probsoltime
                #We write the solving time for the current LP in the file
                self.normtimefile.write(str(probsoltime)+"\n")
                #We update the lpbuilt boolean appropriately depending on wether we could generate the next LP or not
                if nextgentime:
                    lpbuilt = True
                else:
                    lpbuilt = False

        #With this we have generated and solved one problem so we increase the counter
        self.prob_num += 1

        return problemsolvable, proptime, lp_time, soltime