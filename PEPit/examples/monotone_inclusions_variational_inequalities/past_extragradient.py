from PEPit import PEP
from PEPit.functions import ConvexIndicatorFunction
from PEPit.operators import LipschitzStronglyMonotoneOperator
from PEPit.primitive_steps import proximal_step


def wc_past_extragradient(n, gamma, L, verbose=1):
    """
    Consider the monotone variational inequality

        .. math:: \\mathrm{Find}\\, x_\\star \\in C\\text{ such that } \\left<F(x_\\star);x-x_\\star\\right> \\geqslant 0\\,\\,\\forall x\\in C,

    where :math:`C` is a closed convex set and :math:`F` is maximally monotone and Lipschitz.

    This code computes a worst-case guarantee for the **past extragradient method**.
    That, it computes the smallest possible :math:`\\tau(n)` such that the guarantee

        .. math:: \\|x_n - x_{n-1}\\|^2 \\leqslant \\tau(n) \\|x_0 - x_\\star\\|^2,

    is valid, where :math:`x_n` is the output of the **past extragradient method** and :math:`x_0` its starting point.

    **Algorithm**: The past extragradient method is described as follows, for :math:`t \in \\{ 0, \\dots, n-1\\}`,
    
    .. math::
            :nowrap:

            \\begin{eqnarray}
                 \\tilde{x}_{t} & = & \\mathrm{Proj}_{C} [x_t-\\gamma F(\\tilde{x}_{t-1})], \\\\
                 {x}_{t+1} & = & \\mathrm{Proj}_{C} [x_t-\\gamma F(\\tilde{x}_{t})].
            \\end{eqnarray}

    where :math:`\\gamma` is some step-size.

    **Theoretical guarantee**: The method and many variants of it are discussed in [1].
    A worst-case guarantee in :math:`O(1/n)` can be found in [2, 3].
    
    **References**:
    
    `[1] Y.-G. Hsieh, F. Iutzeler, J. Malick, P. Mertikopoulos (2019).
    On the convergence of single-call stochastic extra-gradient methods.
    Advances in Neural Information Processing Systems, 32:6938–6948, 2019
    <https://arxiv.org/pdf/1908.08465.pdf>`_

    `[2] E. Gorbunov, A. Taylor, G. Gidel (2022).
    Last-Iterate Convergence of Optimistic Gradient Method for Monotone Variational Inequalities.
    <https://arxiv.org/pdf/2205.08446.pdf>`_
    
    `[3] Y. Cai, A. Oikonomou, W. Zheng (2022).
    Tight Last-Iterate Convergence of the Extragradient and the Optimistic Gradient Descent-Ascent Algorithm for Constrained Monotone Variational Inequalities.
    <https://arxiv.org/pdf/2204.09228.pdf>`_

    Args:
        n (int): number of iterations.
        gamma (float): the step-size.
        L (float): the Lipschitz constant.
        verbose (int): Level of information details to print.
                        
                        - -1: No verbose at all.
                        - 0: This example's output.
                        - 1: This example's output + PEPit information.
                        - 2: This example's output + PEPit information + CVXPY details.

    Returns:
        pepit_tau (float): worst-case value.
        theoretical_tau (None): no theoretical bound.

    Example:
        >>> pepit_tau, theoretical_tau = wc_past_extragradient(n=5, gamma=1 / 4, L=1, verbose=1)
        (PEPit) Setting up the problem: size of the main PSD matrix: 20x20
        (PEPit) Setting up the problem: performance measure is minimum of 1 element(s)
        (PEPit) Setting up the problem: Adding initial conditions and general constraints ...
        (PEPit) Setting up the problem: initial conditions and general constraints (1 constraint(s) added)
        (PEPit) Setting up the problem: interpolation conditions for 2 function(s)
                         function 1 : Adding 144 scalar constraint(s) ...
                         function 1 : 144 scalar constraint(s) added
                         function 2 : Adding 84 scalar constraint(s) ...
                         function 2 : 84 scalar constraint(s) added
        (PEPit) Compiling SDP
        (PEPit) Calling SDP solver
        (PEPit) Solver status: optimal (solver: SCS); optimal value: 0.06026126041500441
        *** Example file: worst-case performance of the Past Extragradient Method***
                PEPit guarantee:         ||x(n) - x(n-1)||^2 <= 0.0602613 ||x0 - xs||^2

    """

    # Instantiate PEP
    problem = PEP()

    # Declare an indicator function and a monotone operator
    ind_C = problem.declare_function(ConvexIndicatorFunction)
    F = problem.declare_function(LipschitzStronglyMonotoneOperator, mu=0, L=L)

    total_problem = F + ind_C

    # Start by defining its unique optimal point xs = x_*
    xs = total_problem.stationary_point()

    # Then define the starting point x0 of the algorithm and its gradient value g0
    x0 = problem.set_initial_point()

    # Set the initial constraint that is the distance between x0 and x^*
    problem.set_initial_condition((x0 - xs) ** 2 <= 1)

    # Compute n steps of the Proximal Gradient method starting from x0
    x, _, _ = proximal_step(x0, ind_C, gamma)
    xtilde = x
    V = F.gradient(xtilde)
    for _ in range(n):
        xtilde, _, _ = proximal_step(x - gamma * V, ind_C, gamma)
        V = F.gradient(xtilde)
        previous_x = x
        x, _, _ = proximal_step(x - gamma * V, ind_C, gamma)

    # Set the performance metric to the distance between x(n) and x(n-1)
    problem.set_performance_metric((x - previous_x) ** 2)

    # Solve the PEP
    pepit_verbose = max(verbose, 0)
    pepit_tau = problem.solve(verbose=pepit_verbose)

    # Compute theoretical guarantee (for comparison)
    theoretical_tau = None

    # Print conclusion if required
    if verbose != -1:
        print('*** Example file: worst-case performance of the Past Extragradient Method***')
        print('\tPEPit guarantee:\t ||x(n) - x(n-1)||^2 <= {:.6} ||x0 - xs||^2'.format(pepit_tau))

    # Return the worst-case guarantee of the evaluated method ( and the reference theoretical value)
    return pepit_tau, theoretical_tau


if __name__ == "__main__":
    pepit_tau, theoretical_tau = wc_past_extragradient(n=5, gamma=1 / 4, L=1, verbose=1)
