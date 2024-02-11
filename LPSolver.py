import time
import cplex
import cplex.exceptions


def cplexSolve(problem_lp, problem_sol, timeLim):
    """
    Receives a LP file and solves it. It exports the answer to a .sol file and also shows it.
    :param problem_lp: A string with the path of the LP file to solve
    :param problem_sol: A string with the path of the solution file
    :param timeLim: A cutoff time limit for the solver (in seconds)
    :return: A boolean telling if the problem has been solved or not and the time it took to solve it
    """

    #We initialise the return variables
    solved = True
    final_time = 0

    #We try to solve the LP with CPLEX
    try:
        #We set CPLEX parameters
        m=cplex.Cplex(problem_lp)
        m.parameters.timelimit.set(timeLim)
        m.set_log_stream(None)
        m.set_error_stream(None)
        m.set_warning_stream(None)
        m.set_results_stream(None)

        #We solve the problem and compuute the solving time
        start_time = time.time()
        m.solve()
        final_time = time.time()-start_time

        #We write the solution file
        m.solution.write(problem_sol)

    #If there is any CPLEX error and we cannot solve the file we make solved False
    except(cplex.exceptions.CplexError):
        solved = False

    return solved, final_time
