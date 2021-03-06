Positive Definite Matrices
==========================

.. currentmodule:: geotorch

:math:`\operatorname{PSD}(n)` is the manifold of positive definite matrices.

.. math::

    \operatorname{PSD}(n) = \{X \in \mathbb{R}^{n\times n}\:\mid\:X \succ 0\}.

It is realized via an eigenvalue-like factorization:

.. math::

    \begin{align*}
        \pi \colon \operatorname{SO}(n) \times \mathbb{R}^n
                &\to \operatorname{PSD}(n) \\
            (Q, \Lambda) &\mapsto Qf(\Lambda)Q^\intercal
    \end{align*}

where we have identified the vector :math:`\Lambda` with a diagonal matrix in :math:`\mathbb{R}^{n \times n}`. The function :math:`f\colon \mathbb{R} \to (0, \infty)` is applied element-wise to the diagonal. By default, the `softmax` function is used

.. math::

    \begin{align*}
        \operatorname{softmax} \colon \mathbb{R} &\to (0, \infty) \\
            x &\mapsto \log(1+\exp(x)) + \varepsilon
    \end{align*}

where we use a small :math:`\varepsilon > 0` for numerical stability.

.. note::

    For practical applications, it is more convenient to use the class :class:`geotorch.PSSD`, unless the positive definiteness condition is essential. This is because :class:`geotorch.PSSD` is less restrictive, and most of the times it will converge to a max-rank solution anyway, although in the optimization process there might be times when the matrix might become almost singular.

.. autoclass:: PSD

    .. automethod:: sample
    .. automethod:: in_manifold
