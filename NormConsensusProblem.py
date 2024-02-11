import LPSolver
import os
import itertools
import time
from PreferenceGraph import PreferenceGraph

#If this is true we will only save the last generated LP file of each generated problem (this file contains enough information).
#Otherwise we will save all the LPs (which can take a lot of disk space)
DELETE_FILES = True

class NormConsensusProblem:
    """
    Represents a single norm consensus problem. It generates and solves it.
    """

    def __init__(self, numNodes, RelPer, numUsers, PrefProb, appProb, probnumber, lpdir, soldir):
        #The number of nodes in the preference graph
        self.numnodes = numNodes
        #The percentage of generalisation relations out of all possible in the graph
        self.relper = RelPer
        #The number of users
        self.numusers= numUsers
        #The probability of knowing the preference of a user to a node
        self.prefprob = PrefProb
        #The probability of a known preference to be an approval one
        self.appprob = appProb
        #The preference graph of the problem
        self.graph = PreferenceGraph()
        #The problem id
        self.probnumber = probnumber
        #The number of solutions found so far
        self.iternumber = 0
        #The LP file to be solved (once it has been generated)
        self.tosolve = None
        #The sign we are solving first (+ for positive consensus - for negative)
        self.signsymb = "+"
        #The directory of the LP files
        self.lpdir = lpdir
        #The directory of the solution files
        self.soldir = soldir

    def generateGraph(self):
        """
        Generates the graph of the norm consensus problem
        :return: The time it took to propagate the preferences in the graph (which is part of the overall solving time)
        """

        #We generate the graph
        self.graph = PreferenceGraph()
        self.graph.generate(self.numnodes, self.relper, self.numusers, self.prefprob, self.appprob)

        #We propagate appropriateness and inappropriateness (as this is part of the solving of the problem
        #we calculate the time it took to add it to the overall solving time)
        start_time = time.time()
        self.graph.propagate()
        final_time = time.time() - start_time

        return final_time

    def buildLp(self, sign):
        """
        Builds the LP file to solve the problem (note there is a separate LP file for positive and negative consensus)
        :param sign: 1 if we are building the positive consensus LP file, -1 for the negative consensus LP
        :return:
        """

        #we prepare a list for the binary variables of the LP
        binaries = []

        #If we are dealing with negative consensus we have to reinitialise the iteration counter and change the sign
        if sign == -1:
            self.iternumber = 0
            self.signsymb = "-"

        #We create and opern the LP file
        filename = self.lpdir+"Problem" + str(self.probnumber) + self.signsymb + "_" + str(self.iternumber) + ".lp"
        returnfile = filename
        f = open(filename, "w")

        #We find the appropriate search space
        if sign == 1:
            searchspace = self.graph.positivesearchspace()
        else:
            searchspace = self.graph.negativesearchspace()

        #If there are nodes in the searchspace we will write the LP
        if searchspace:

            #First, the target function
            f.write("Minimize\n")
            target_function = ""
            #For each node in the search space we calclate its coefficient (as defined in the paper)
            for n in searchspace:
                coef = 1
                for p in n.getparents():
                    if p in searchspace:
                        coef += 1
                #We add the node to the function and to the list of binaries
                target_function += str(coef)+"n"+str(n.getid())+ " + "
                binaries.append("n"+str(n.getid()))
            #We remove the additional " + " and write the formula in the LP file
            target_function = target_function[:len(target_function)-3]
            f.write(target_function+"\n")

            #Now we write the costraints
            f.write("Subject to\n")
            #First, the coverage constraints
            retdict = self.graph.nodesUser(sign, searchspace)
            #For each user we write its coverage constraint (as defined in the paper)
            #If the user cannot be "covered" then the problem is unsolvable, so we are not going to return any LP file
            #Once a user cannot be covered the LP generation process stops
            for u in retdict.keys():
                if returnfile:
                    covconstraint = ""
                    for id in retdict[u]:
                        covconstraint += "n"+str(id)+" + "
                    if len(covconstraint) > 0:
                        covconstraint = covconstraint[:len(covconstraint)-2]+">= 1"
                        f.write(covconstraint+"\n")
                    else:
                        returnfile = None
            #If we could write the constraints for all users
            if returnfile:
                #We will now write the generalisation relation constraints (as defined in the paper)
                for n in searchspace:
                    for s in n.getsiblings():
                        if s in searchspace:
                            genconstraint = "n"+str(n.getid())+" + n"+str(s.getid())+" <= 1\n"
                            f.write(genconstraint)
                #Finally we write the list of binary variables and finish the LP
                #Note that since we have not solved the LP yet we are not adding solution constraints
                f.write("Binaries\n")
                for b in binaries:
                    f.write(b+"\n")
                f.write("End")

        #If the searchsaapce is empty we will not generate the LP
        else:
            returnfile = None

        #The next LP to solve is the one we just generated or None if we could not generate it
        f.close()
        self.tosolve = returnfile

        #If the LP file we generated cannot be solved we delete it
        if not returnfile:
            os.remove(filename)

        return returnfile

    def nextLp(self, solfilename):
        """
        Once an LP file is solved, this function takes the solution and adds the corresponding solution constraint
        to the LP so we can find the next solution
        :param solfilename: The path of the solution file
        :return: The path of the next LP to solve or None if the previous LP could not be solved
        """

        #We open the solution file and navigate it to retrive the nodes that are part of the solution
        solfile = open(solfilename, "r")
        lines = solfile.readlines()
        read = False
        solution = []
        vars = []
        for l in lines:
            if "</variables>" in l:
                read = False
            elif read:
                l.replace(" ", "")
                l.replace("\n", "")
                elem = l.split("\"")
                vars.append(elem[1])
                if elem[5] == "1":
                    solution.append(elem[1])
            elif "<variables>" in l:
                read = True
        solfile.close()

        #If the solution is not empty (in other words, if the LP file could be solved)
        #We build the solution constraint as defined in the paper. Note that the constraint in the paper
        #contains a min function, hence we have to linearise it, thus generating more than one constraint
        #In this case we generate all the linear combinations that can happen from the non-linear constraint
        #Note though that other linearisation techniques are possible, which could even improve the solving times
        if solution:
            solconstelems = {}
            for var in solution:
                solconstelems[var] = [var]
                id = int(var.replace("n", ""))
                for s in self.graph.getnode(id).getsiblings():
                    if s.getid() in vars:
                        solconstelems[var].append(s)
            allsolconstids = list(itertools.product(*solconstelems.values()))

            #Now we open the new LP file (the next iteration of the same problem)
            self.iternumber += 1
            newfilename = self.lpdir+"Problem"+ str(self.probnumber) + self.signsymb + "_"+ str(self.iternumber) + ".lp"
            pastlp = open(self.tosolve, "r")
            newlp = open(newfilename, "w")
            # We copy the old LP file's contents and delete it (if this setting is activated)
            pastlines = pastlp.readlines()
            if DELETE_FILES:
                os.remove(self.tosolve)
                os.remove(solfilename)

            #We write the all the lines of the previous LP file into the new one up until the end of the block of
            #constraints (once we find "Binaries")
            for l in pastlines:
                if "Binaries" in l:
                    #We add the new solution constraints
                    for setsol in allsolconstids:
                        solconst = ""
                        for var in setsol:
                            solconst += var + " + "
                        solconst = solconst[:len(solconst)-2]+"<="+str(len(solution)-1)
                        newlp.write(solconst+"\n")
                newlp.write(l)
            #The next file to solve in the new LP
            self.tosolve = newfilename

        #If there was no solution then there is no new LP file to solve
        else:
            self.tosolve = None

        return self.tosolve

    def solveone(self):
        """
        Solves one iteration of the norm consensus problem and generates the next LP
        :return: The time in seconds it took to solve the current LP, and the time it took to generate the next one
        """

        # We initialise the times to 0 in case there is no problem to solve
        nextgentime = 0
        solvetime = 0

        #If there is a problem to solve
        if self.tosolve:
            #We build the path for the solution file
            solfilename = self.tosolve
            solfilename = solfilename.replace("LPs", "SOLs").replace(".lp", ".sol")

            #We solve the problem and get the solving time
            solved, solvetime = LPSolver.cplexSolve(self.tosolve, solfilename, 3600)

            #If the problem could be solved (no errors happend while solving) we generate the next LP and record the time
            if solved:
                start_time = time.time()
                self.nextLp(solfilename)
                nextgentime = time.time() - start_time

        return solvetime, nextgentime