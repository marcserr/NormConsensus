## Norm Consensus

This code can be used to replicate the experiments in the AAMAS 2024 paper "Multi-user norm consensus". The code tests the algorithm presented in the paper to find consensus among multiple users' preferences. It will generate norm consensus problems with different parameters and save the time it takes to solve them. These times can then be used to calculate the numbers and draw the figures in the paper. Depending on the computer used to run the tests, the results will differ, for the paper we used a standard 2018 13'' MacBook Pro (Intel Core i5-8259U processor, 8Gb of RAM, running Mac OS 12.6.). 

### Contents

The "doc" directory in this repository contains supplementary material for the AAMAS 2024 paper, in particular, the full proofs for the lemmas and theorems presented. The TestData directory contains the results for our run of the tests.

### Requirements:

The code has to be executed in Python3, it requires numpy and cplex to be installed. Cplex is available for academics on the IBM website.

The code saves the last LP for each generated problem (to save space it deletes previous LPs), therefore it needs to have a directory named "TestData" on the same directory where main.py and the rest of Python files are. Inside TestData there must be two other directories called "LPs" and "SOLs".

This code was executed in Mac OS 12.6, since it navigates the folders where it is executed it is possible that it needs to be udapted for other operating systems.

### How to use:

Open a terminal in the directory where main.py is, run "python3 main.py". 
The code will perform all experiments as described in the paper automatically and does not need any other input. 
Note the whole run of tests may take some hours to finish (close to 10h in our case)

Once the code finishes you can find the results in the TestData folder.

The file "problemsoltime.txt" contains each of the solving times for each of the generated BIP files (solving each of these BIP files results in finding one consensus)

The file "testdata.txt" contains the overall solving times for each generated problem, it separates problems into blocks depending on the variables used to generate the problems (for example, TEST5U100N0G5P is the heading of the block of tests with 5 users, 100 nodes, 0 generalisation percentage, and 5 preference percentage). Each of the following lines provides the solving time for each of the problems. Form left to write it specifies the problem number, the consensus that were found for the problem (+- for both positive and negative, + only positive, - only negative, ns for no consensus solution), the overall solving time of the problem, the time it took to propagate the preferences in the graph, the lp building time, and the lp solving time. For example, "Problem3(+-):2.325756788253784(0.0001590251922607422, 0.05085587501525879,2.2747418880462646)" means problem 3 had both positive and negative consensus (+-) it took 2.325756788253784 seconds to solve of which 0.0001590251922607422 were to propagate preferences, 0.05085587501525879 to build the lp, and 2.2747418880462646 to solve it.

To generate the image map in the paper run "map.py" it will save the image in "ConfigTimes.pdf".
To obtain some general results (mean solving time for each LP, std. deviation of this mean maximum solving time in any LP, total solving time of all tests) of the tests run "results.py".
