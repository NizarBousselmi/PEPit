from PEPit import PEP
from PEPit.functions import SmoothStronglyConvexQuadraticFunction
import numpy as np

def wc_gradient_descent_quadratics(mu, L, gamma, n, verbose=1):
    """
    Consider the convex minimization problem

    .. math:: f_\\star \\triangleq \\min_x f(x),

    where :math:`f=\\frac{1}{2} x^T Q x` is :math:`L`-smooth and :math:`\\mu`-strongly convex (i.e. :math:`\\mu I \\preceq Q \\preceq LI`).

    This code computes a worst-case guarantee for **gradient descent** with fixed step-size :math:`\\gamma`.
    That is, it computes the smallest possible :math:`\\tau(n, \\mu, L, \\gamma)` such that the guarantee

    .. math:: f(x_n) - f_\\star \\leqslant \\tau(n, \\mu, L, \\gamma) \\|x_0 - x_\\star\\|^2

    is valid, where :math:`x_n` is the output of gradient descent with fixed step-size :math:`\\gamma`, and
    where :math:`x_\\star` is a minimizer of :math:`f`.

    In short, for given values of :math:`n`, :math:`\\mu`, :math:`L`, and :math:`\\gamma`, :math:`\\tau(n, L, \\gamma)` is computed as the worst-case
    value of :math:`f(x_n)-f_\\star` when :math:`\\|x_0 - x_\\star\\|^2 \\leqslant 1`.

    **Algorithm**:
    Gradient descent is described by

    .. math:: x_{t+1} = x_t - \\gamma \\nabla f(x_t),

    where :math:`\\gamma` is a step-size.
    
    **Theoretical guarantee**:
    When :math:`\\gamma \\leqslant \\frac{2}{L}` and :math:`0 \\leqslant \\mu \\leqslant L `, the **tight** theoretical guarantee can be
    found in [1, Equation (4.17)] (it is a conjecture in this work but it is provable):

    .. math:: f(x_n)-f_\\star \\leqslant \\frac{L}{2} \\max\\{\\alpha(1-\\alpha L\\gamma)^{2n}, (1-L\\gamma)^{2n} \\} \\|x_0-x_\\star\\|^2,

    where :math:`\\alpha = \\mathrm{proj}_{[\\frac{\\mu}{L},1]} (\\frac{1}{L\\gamma (2n+1)}) `.

    **References**:

    `[1] N. Bousselmi, J. Hendrickx, F. Glineur  (2023).
    Interpolation Conditions for Linear Operators and applications to Performance Estimation Problems.
    arXiv preprint
    <https://arxiv.org/pdf/2302.08781.pdf>`_

    Args:
        mu (float): the strong convexity parameter.
        L (float): the smoothness parameter.
        gamma (float): step-size.
        n (int): number of iterations.
        verbose (int): Level of information details to print.
                        
                        - -1: No verbose at all.
                        - 0: This example's output.
                        - 1: This example's output + PEPit information.
                        - 2: This example's output + PEPit information + CVXPY details.

    Returns:
        pepit_tau (float): worst-case value
        theoretical_tau (float): theoretical value
        
    Example:
        >>> L = 3.
        >>> mu = 0.3
        >>> pepit_tau, theoretical_tau = wc_gradient_descent_quadratics(mu=mu, L=L, gamma=1 / L, n=4, verbose=1)
        (PEPit) Setting up the problem: size of the main PSD matrix: 7x7
        (PEPit) Setting up the problem: performance measure is minimum of 1 element(s)
        (PEPit) Setting up the problem: Adding initial conditions and general constraints ...
        (PEPit) Setting up the problem: initial conditions and general constraints (1 constraint(s) added)
        (PEPit) Setting up the problem: interpolation conditions for 1 function(s)
                         function 1 : Adding 36 scalar constraint(s) ...
                         function 1 : 36 scalar constraint(s) added
                         function 1 : Adding 1 lmi constraint(s) ...
                         Size of PSD matrix 1: 6x6
                		   function 1 : 1 lmi constraint(s) added
        (PEPit) Setting up the problem: constraints for 0 function(s)
        (PEPit) Compiling SDP
        (PEPit) Calling SDP solver
        (PEPit) Solver status: optimal (solver: MOSEK); optimal value: 0.06495738898558603
        *** Example file: worst-case performance of gradient descent on quadratics with fixed step-sizes ***
        	PEPit guarantee:	    f(x_n)-f_* <= 0.0649574 ||x_0 - x_*||^2
        	Theoretical guarantee:	 f(x_n)-f_* <= 0.0649574 ||x_0 - x_*||^2

    """

    # Instantiate PEP
    problem = PEP()

    # Declare a strongly convex smooth function
    func = problem.declare_function(SmoothStronglyConvexQuadraticFunction, mu=mu, L=L)

    # Start by defining its unique optimal point xs = x_* and corresponding function value fs = f_*
    xs = func.stationary_point()
    fs = func(xs)

    # Then define the starting point x0 of the algorithm
    x0 = problem.set_initial_point()

    # Set the initial constraint that is the distance between x0 and x^*
    problem.set_initial_condition((x0 - xs) ** 2 <= 1)

    # Run n steps of the GD method
    x = x0
    for _ in range(n):
        x = x - gamma * func.gradient(x)

    # Set the performance metric to the function values accuracy
    problem.set_performance_metric(func(x) - fs)

    # Solve the PEP
    pepit_verbose = max(verbose, 0)
    pepit_tau = problem.solve(verbose=pepit_verbose)
    
    # Compute theoretical guarantee (for comparison)
    t = 1 / (L*gamma*(2*n+1))
    if t < mu/L:
        alpha = mu/L
    elif t > 1:
        alpha = 1
    else:
        alpha = t
        
    theoretical_tau = 0.5*L*np.max((alpha*(1-alpha*L*gamma)**(2*n),(1-L*gamma)**(2*n)))

    # Print conclusion if required
    if verbose != -1:
        print('*** Example file: worst-case performance of gradient descent on quadratics with fixed step-sizes ***')
        print('\tPEPit guarantee:\t f(x_n)-f_* <= {:.6} ||x_0 - x_*||^2'.format(pepit_tau))
        print('\tTheoretical guarantee:\t f(x_n)-f_* <= {:.6} ||x_0 - x_*||^2'.format(theoretical_tau))
        
    # Return the worst-case guarantee of the evaluated method
    return pepit_tau, theoretical_tau


if __name__ == "__main__":
    L = 3
    mu = 0.3
    pepit_tau, theoretical_tau = wc_gradient_descent_quadratics(mu=mu, L=L, gamma=1 / L, n=4, verbose=1)
