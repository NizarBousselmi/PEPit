import numpy as np

from PEPit.pep import PEP
from PEPit.Function_classes.smooth_strongly_convex_function import SmoothStronglyConvexFunction


def wc_heavyball(mu, L, alpha, beta, n):
    """
    In this example, we use the heavy ball method for solving the L-smooth
    convex minimization problem
    min_x F(x);
    for notational convenience we denote xs = argmin_x F(x), where F(x) is L-smooth and convex.
    The heavy-ball method is defined as follows :
    x_{k+1} = x_k - alpha*grad(f(x_k)) - beta*(x_k-x_{k-1})

    We show how to compute the worst-case value of F(xN)-F(xs) when xN is obtained by doing N steps
    of the method starting with an initial iterate satisfying ||x0-xs||<=1.

    This methods was first introduce in [1], and convergence upper bound was proved in [2].
    [1] B.T. Polyak.
    "Some methods of speeding up the convergence of iteration methods".
    [2]  Euhanna Ghadimi, Hamid Reza Feyzmahdavian, Mikael. Johansson.
    " Global convergence of the Heavy-ball method for convex optimization".

    :param L: (float) the smoothness parameter.
    :param mu: (float) the strong convexity parameter.
    :param alpha: (float) parameter of the scheme.
    :param beta: (float) parameter of the scheme such that 0<beta<1 and 0<alpha<2*(1+beta)
    :param n: (int) number of iterations.
    :return:
    """


    # Instantiate PEP
    problem = PEP()

    # Declare a convex lipschitz function
    func = problem.declare_function(SmoothStronglyConvexFunction,
                                    {'mu': mu, 'L': L})

    # Start by defining its unique optimal point and its function value
    xs = func.optimal_point()
    fs = func.value(xs)

    # Then Define the starting point of the algorithm
    x0 = problem.set_initial_point()

    # Set the initial constraint that is the distance between x0 and x^*
    problem.set_initial_condition((x0 - xs) ** 2 <= 1)

    # Run the heavy ball method
    x_old = x0
    g_old = func.gradient(x_old)
    x_new = x_old - 1/L*alpha*g_old
    g_new = func.gradient(x_new)

    for _ in range(n):
        x_new, x_old = x_new - alpha/L*g_new + beta*(x_new - x_old), x_new
        g_new = func.gradient(x_new)

    # Set the performance metric to the final distance to optimum
    problem.set_performance_metric(func.value(x_new)-fs)

    # Solve the PEP
    wc = problem.solve()

    # Theoretical guarantee (for comparison)
    print('*** Example file: worst-case performance of the heavy-ball method (HBM) in function values ***')
    print('\tPEP-it guarantee:\t f(y_n)-f_* <= ', wc)
    #print('\tTheoretical guarantee:\t f(y_n)-f_* <= ', theory)
    # Return the worst-case guarantee of the evaluated method (and the upper theoretical value)

    # Return the rate of the evaluated method
    return wc


if __name__ == "__main__":

    mu = 0.1
    L = 1.
    ## Test scheme parameters
    #alpha = 1
    #beta = 1/2
    ## Optimal parameters
    alpha = 4*L/(np.sqrt(L)+np.sqrt(mu))**2
    beta = ((np.sqrt(L)-np.sqrt(mu))/(np.sqrt(L)+np.sqrt(mu)))**2
    n = 1

    rate = wc_heavyball(mu=mu,
                        L=L,
                        alpha=alpha,
                        beta=beta,
                        n=n)