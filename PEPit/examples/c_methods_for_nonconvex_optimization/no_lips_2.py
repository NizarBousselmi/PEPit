import numpy as np

from PEPit.pep import PEP
from PEPit.functions.convex_function import ConvexFunction
from PEPit.functions.convex_indicator import ConvexIndicatorFunction
from PEPit.primitive_steps.bregman_gradient_step import bregman_gradient_step


def wc_no_lips2(L, gamma, n, verbose=True):
    """
    Consider the constrainted composite convex minimization problem

        .. math:: \min_x { F(x) = f_1(x) + f_2(x) }

    where :math:`f_2` is a closed convex indicator function and :math:`f_1` is :math:`L`-smooth relatively to :math:`h` (possibly non-convex),
    and :math:`h` is closed proper and convex.

    This code computes a worst-case guarantee for the **NoLips method** solving this problem.
    That is, it computes the smallest possible :math:`\\tau(n,L)` such that the guarantee

        .. math:: \min_n (D_h(x_n, x_*)) \\leqslant \\tau(n,L) * (F(x_0) - F(x_n))

    is valid, where :math:`x_n` is the output of the **NoLips method**, and where :math:`x_0` is the starting point of :math:`F`,
    and where :math:`D_h` is the Bregman distance generated by :math:`h`,that is :math:` D_h(x, y) = h(x) - h(y) - \\nabla h (y)^T(x - y)`.

    **Algorithms**:

        .. math:: x_{n+1} = \\arg\\min_{u \\in R^n} \\nabla f(x_n)^T(u - x_n) + \\frac{1}{\\gamma} D_h(u, x_n)

        .. math:: D_h(x_{n+1}, x_{n}) = h(x_{n+1}) - h(x_{n}) - \\nabla h (x_{n+1})^T(x_{n+1} - x_{n})

    **Theoretical guarantees**:

    The theoretical **tight** bound is obtained in [1, Proposition 4.1],

        .. math:: \\tau(n, L, \\gamma) = \\frac{\\gamma}{n}

    **References**:

    The detailed approach is availaible in [1], and the PEP approach is presented in [2].

    [1] Jérôme Bolte, Shoham Sabach, Marc Teboulle, and Yakov Vaisbourd. First Order Methods Beyond
    Convexity and Lipschitz Gradient Continuity with Applications to Quadratic Inverse Problems. SIAM
    Journal on Optimization.

    [2] Radu-Alexandru Dragomir, Adrien B. Taylor, Alexandre d’Aspremont, and
    Jérôme Bolte. "Optimal Complexity and Certification of Bregman
    First-Order Methods". (2019)

    DISCLAIMER: This example requires some experience with PESTO and PEPs
    (see Section 4 in [2]).

    Args:
        L (float): relative-smoothness parameter
        gamma (float): step size (equal to :math:`\\frac{1}{2L}` for guarantee)
        n (int): number of iterations.
        verbose (bool, optional): if True, print conclusion.

    Returns:
        tuple: worst_case value, theoretical value

    Example:
        >>> pepit_tau, theoretical_tau = wc_no_lips2(1, 1, 3)
        (PEP-it) Setting up the problem: size of the main PSD matrix: 13x13
        (PEP-it) Setting up the problem: performance measure is minimum of 3 element(s)
        (PEP-it) Setting up the problem: initial conditions (1 constraint(s) added)
        (PEP-it) Setting up the problem: interpolation conditions for 3 function(s)
                 function 1 : 56 constraint(s) added
                 function 2 : 42 constraint(s) added
                 function 3 : 25 constraint(s) added
        (PEP-it) Compiling SDP
        (PEP-it) Calling SDP solver
        (PEP-it) Solver status: optimal (solver: SCS); optimal value: 0.3333330898981533
        *** Example file: worst-case performance of the NoLips_2 in Bregman distance ***
            PEP-it guarantee:	 min_n Dh(y_n, y_(n-1)) <= 0.333333 Dh(y_0, x_*)
            Theoretical guarantee :	 min_n Dh(y_n, y_(n-1)) <= 0.333333 Dh(y_0, x_*)
    """

    # Instantiate PEP
    problem = PEP()

    # Declare two convex functions and a convex function
    d1 = problem.declare_function(ConvexFunction,
                                  param={}, is_differentiable=True)
    d2 = problem.declare_function(ConvexFunction,
                                  param={}, is_differentiable=True)
    func1 = (d2 - d1) / 2
    h = (d1 + d2) / L / 2
    func2 = problem.declare_function(ConvexIndicatorFunction,
                                     param={'D': np.inf})

    # Define the function to optimize as the sum of func1 and func2
    func = func1 + func2

    # Then define the starting point x0 of the algorithm and its function value f0
    x0 = problem.set_initial_point()
    gh0, h0 = h.oracle(x0)
    gf0, f0 = func1.oracle(x0)
    _, F0 = func.oracle(x0)

    # Compute n steps of the NoLips starting from x0
    x1, x2 = x0, x0
    gfx = gf0
    ghx = gh0
    hx1, hx2 = h0, h0
    for i in range(n):
        x2, _, _ = bregman_gradient_step(gfx, ghx, func2 + h, gamma)
        gfx, _ = func1.oracle(x2)
        ghx, hx2 = h.oracle(x2)
        Dhx = hx1 - hx2 - ghx * (x1 - x2)
        # update the iterates
        x1, hx1 = x2, hx2
        # Set the performance metric to the Bregman distance to the last iterate
        problem.set_performance_metric(Dhx)
    _, Fx = func.oracle(x2)
    # Set the initial constraint that is the Bregman distance between x0 and x^*
    problem.set_initial_condition(F0 - Fx <= 1)

    # Solve the PEP
    pepit_tau = problem.solve(verbose=verbose)

    # Compute theoretical guarantee (for comparison)
    theoretical_tau = gamma / n

    # Print conclusion if required
    if verbose:
        print('*** Example file: worst-case performance of the NoLips_2 in Bregman distance ***')
        print('\tPEP-it guarantee:\t min_n Dh(y_n, y_(n-1)) <= {:.6} Dh(y_0, x_*)'.format(pepit_tau))
        print('\tTheoretical guarantee :\t min_n Dh(y_n, y_(n-1)) <= {:.6} Dh(y_0, x_*) '.format(theoretical_tau))

    # Return the worst-case guarantee of the evaluated method (and the upper theoretical value)
    return pepit_tau, theoretical_tau


if __name__ == "__main__":
    L = 1
    gamma = 1 / L
    n = 3

    pepit_tau, theoretical_tau = wc_no_lips2(L=L,
                                             gamma=gamma,
                                             n=n)
