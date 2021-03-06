Low Rank Matrices
=================

.. currentmodule:: geotorch

:math:`\operatorname{LowRank}(n,k,r)` is the algebraic variety of matrices of rank less or equal
to :math:`r`, for a given :math:`r \leq \min\{n, k\}`:

.. math::

    \operatorname{LowRank}(n,k,r) = \{X \in \mathbb{R}^{n\times k}\:\mid\:\operatorname{rank}(X) \leq r\}

It is realized via an SVD-like factorization:

.. math::

    \begin{align*}
        \pi \colon \operatorname{St}(n,r) \times \mathbb{R}^r \times \operatorname{St}(k, r)
                &\to \operatorname{LowRank}(n,k,r) \\
            (U, \Sigma, V) &\mapsto U\Sigma V^\intercal
    \end{align*}

where we have identified the vector :math:`\Sigma` with a diagonal matrix in :math:`\mathbb{R}^{r \times r}`.

.. autoclass:: LowRank

    .. automethod:: sample
    .. automethod:: in_manifold
