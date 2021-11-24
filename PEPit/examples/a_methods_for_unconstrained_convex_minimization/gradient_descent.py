from PEPit.pep import PEP
from PEPit.functions.smooth_strongly_convex_function import SmoothStronglyConvexFunction


def wc_gd(L, gamma, n, verbose=True):
    """
    Consider the minimization problem

    .. math:: f_\star = \\min_x f(x),

    where :math:`f` is :math:`L`-smooth and convex.

    This code computes a worst-case guarantee for **gradient descent** with fixed step size :math:`\\gamma`. That is, it computes
    the smallest possible :math:`\\tau(n, L, \\gamma)` such that the guarantee

    .. math:: f(x_n) - f_\star \\leqslant \\tau(n, L, \\gamma)  || x_0 - x_\star ||^2

    is valid, where :math:`x_n` is the output of gradient descent with fixed step size :math:`\\gamma`, and
    where :math:`x_\star` is a minimizer of :math:`f`.

    In short, for given values of :math:`n`, :math:`L`, and :math:`\\gamma`, :math:`\\tau(n, L, \\gamma)` is computed as the worst-case
    value of :math:`f(x_n)-f_\star` when :math:`||x_0 - x_\star||^2 \\leqslant 1`.

    **Algorithm**:
    Gradient descent is described by

    .. math:: x_{k+1} = x_k - \\gamma \\nabla f(x_k),

    where :math:`\\gamma` is a step size.

    **Theoretical guarantee**:
    When :math:`\\gamma=\\frac{1}{L}`, the tight theoretical guarantee can be found in [1, Theorem 1]:

    .. math:: f(x_n)-f_\\star \\leqslant \\frac{L||x_0-x_\\star||^2}{4n+2}.

    **References**:
    [1] Y. Drori, M. Teboulle (2014). Performance of first-order methods for smooth convex minimization: a novel
    approach. Math. Program. 145(1–2), 451–482.


    :param L: (float) the smoothness parameter.
    :param gamma: (float) step size.
    :param n: (int) number of iterations.
    :param verbose: (bool) if True, print conclusion

    :return: (tuple) worst_case value, theoretical value

    Example:
        >>> L, n = 3, 4
        >>> pepit_tau, theoretical_tau = inGD.wc_gd(L=L, gamma=1/L, n=n, verbose=True)
        (PEP-it) Setting up the problem: size of the main PSD matrix: 7x7
        (PEP-it) Setting up the problem: performance measure is minimum of 1 element(s)
        (PEP-it) Setting up the problem: initial conditions (1 constraint(s) added)
        (PEP-it) Setting up the problem: interpolation conditions for 1 function(s)
		         function 1 : 30 constraint(s) added
        (PEP-it) Compiling SDP
        (PEP-it) Calling SDP solver
        (PEP-it) Solver status: optimal (solver: MOSEK); optimal value: 0.16666666497937685
        *** Example file: worst-case performance of gradient descent with fixed step sizes ***
	        PEP-it guarantee:       f(x_n)-f_* <= 0.166667 ||x_0 - x_*||^2
	        Theoretical guarantee:  f(x_n)-f_* <= 0.166667 ||x_0 - x_*||^2
    """

    # Instantiate PEP
    problem = PEP()

    # Declare a strongly convex smooth function
    func = problem.declare_function(SmoothStronglyConvexFunction, param={'mu': 0, 'L': L})

    # Start by defining its unique optimal point xs = x_* and corresponding function value fs = f_*
    xs = func.stationary_point()
    fs = func.value(xs)

    # Then define the starting point x0 of the algorithm
    x0 = problem.set_initial_point()

    # Set the initial constraint that is the distance between x0 and x^*
    problem.set_initial_condition((x0 - xs) ** 2 <= 1)

    # Run n steps of the GD method
    x = x0
    for _ in range(n):
        x = x - gamma * func.gradient(x)

    # Set the performance metric to the function values accuracy
    problem.set_performance_metric(func.value(x) - fs)

    # Solve the PEP
    pepit_tau = problem.solve(verbose=verbose)

    # Compute theoretical guarantee (for comparison)
    theoretical_tau = L / (2 * (2 * n + 1))

    # Print conclusion if required
    if verbose:
        print('*** Example file: worst-case performance of gradient descent with fixed step sizes ***')
        print('\tPEP-it guarantee:\t\t f(x_n)-f_* <= {:.6} ||x_0 - x_*||^2'.format(pepit_tau))
        print('\tTheoretical guarantee:\t f(x_n)-f_* <= {:.6} ||x_0 - x_*||^2'.format(theoretical_tau))

    # Return the worst-case guarantee of the evaluated method (and the reference theoretical value)
    return pepit_tau, theoretical_tau


if __name__ == "__main__":
    n = 2
    L = 1
    gamma = 1 / L

    wc = wc_gd(L=L,
               gamma=gamma,
               n=n)
