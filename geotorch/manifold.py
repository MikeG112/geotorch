import torch
import torch.nn as nn

import geotorch.parametrize as P


class AbstractManifold(P.Parametrization):
    def __init__(self, dimensions, size):
        super().__init__()
        if dimensions != "product" and (
            not isinstance(dimensions, int) or dimensions < 0
        ):
            raise ValueError(
                "dimensions should be a non-negative integer or 'product'. Got {}".format(
                    dimensions
                )
            )

        self.transpose = False
        self.dimensions = dimensions
        if self.dimensions == "product":
            self.tensorial_size = tuple()
        else:
            self.tensorial_size = tuple(size[:-dimensions])

        if self.dimensions == "product":
            self.dim = size
        elif self.dimensions == 1:
            self.n = size[-1]
            self.dim = (self.n,)
        elif self.dimensions == 2:
            self.n, self.k = size[-2], size[-1]
            self.transpose = self.n < self.k
            if self.transpose:
                self.n, self.k = self.k, self.n
            self.dim = (self.n, self.k)
        else:  # self.dimensions >= 3
            self.dim = tuple(size[-(i + 1)] for i in reversed(range(self.dimensions)))

    @property
    def orig_dim(self):
        self.dim[::-1] if self.transpose else self.dim

    def extra_repr(self):
        if self.dimensions == 1:
            ret = "n={}".format(self.n)
        elif self.dimensions == 2:
            ret = "n={}, k={}".format(self.n, self.k)
        else:
            ret = "dim={}".format(self.dim)
        if len(self.tensorial_size) != 0:
            ret += ", tensorial_size={}".format(self.tensorial_size)
        return ret


class EmbeddedManifold(AbstractManifold):
    def projection(self, X):  # pragma: no cover
        r"""
        Parametrizes the manifold in terms of a projection from the ambient space
        Args:
            X (torch.nn.Tensor): A tensor in the ambient space
        Returns:
            tensor (torch.nn.Tensor): A tensor on the manifold
        Note:
            This function should be surjective, otherwise not all the manifold
            will be explored
        """
        raise NotImplementedError()

    def forward(self, X):
        if self.transpose:
            X = X.transpose(-2, -1)
        X = self.projection(X)
        if self.transpose:
            X = X.transpose(-2, -1)
        return X


class Manifold(AbstractManifold):
    def __init__(self, dimensions, size):
        super().__init__(dimensions, size)
        self.register_buffer("base", torch.empty(*size))
        if self.transpose:
            self.base = self.base.transpose(-2, -1)

    def trivialization(self, X, B):  # pragma: no cover
        r"""
        Parametrizes the manifold in terms of a tangent space
        Args:
            X (torch.nn.Tensor): A tensor, usually living in T_B M
            B (torch.nn.Tensor): Point on M at whose tangent space we are trivializing
        Returns:
            tensor (torch.nn.Tensor): A tensor on the manifold
        Note:
            This function should be surjective, otherwise not all the manifold
            will be explored
        """
        raise NotImplementedError()

    def forward(self, X):
        if self.transpose:
            X = X.transpose(-2, -1)
        X = self.trivialization(X, self.base)
        if self.transpose:
            X = X.transpose(-2, -1)
        return X

    def update_base(self, X=None):
        is_registered = self.is_registered()
        if not is_registered and X is None:
            raise ValueError(
                "Cannot update the base before registering the Parametrization"
            )
        with torch.no_grad():
            if X is None:
                X = self.evaluate()
            else:
                X = self.evaluate(X)
            if self.transpose:
                X = X.transpose(-2, -1)
            self.base.data.copy_(X)
            if is_registered:
                self.last_parametrization().originals[0].zero_()


class Fibration(AbstractManifold):
    def __init__(self, dimensions, size, total_space):
        super().__init__(dimensions, size)
        if not isinstance(total_space, AbstractManifold):
            raise TypeError(
                "Expecting total_space to be a subclass "
                "'geotorch.AbstractManifold'. Got '{}''.".format(
                    type(total_space).__name__
                )
            )

        f_embedding = self.embedding
        if self.transpose:

            def f_embedding(_, X):
                return self.embedding(X.transpose(-2, -1))

        Embedding = type(
            "Embedding" + self.__class__.__name__,
            (P.Parametrization,),
            {"forward": f_embedding},
        )

        total_space.chain(Embedding())
        self.chain(total_space)

    def embedding(self, *X):  # pragma: no cover
        raise NotImplementedError()

    def fibration(self, *X):  # pragma: no cover
        raise NotImplementedError()

    def forward(self, *Xs):
        X = self.fibration(*Xs)
        if self.transpose:
            X = X.transpose(-2, -1)
        return X

    # Expose the parameters from total_space
    @property
    def total_space(self):
        return self.parametrizations.originals

    @property
    def base(self):
        return self.total_space.base

    def update_base(self, *Xs):
        self.total_space.update_base(*Xs)


class ProductManifold(AbstractManifold):
    def __init__(self, manifolds):
        super().__init__(dimensions="product", size=ProductManifold._size(manifolds))
        self.manifolds = nn.ModuleList(manifolds)

    @staticmethod
    def _size(manifolds):
        for mani in manifolds:
            if not isinstance(mani, AbstractManifold):
                raise TypeError(
                    "Expecting all elements in a ProductManifold to be "
                    "geotorch.AbstractManifold. Found a {}.".format(type(mani).__name__)
                )

        return tuple(m.dim for m in manifolds)

    def forward(self, *Xs):
        return tuple(mani.evaluate(X) for mani, X in zip(self, Xs))

    def update_base(self, Xs=None):
        is_registered = self.is_registered()
        if not is_registered and Xs is None:
            raise ValueError(
                "Cannot update the base before registering the " "Parametrization"
            )
        with torch.no_grad():
            if Xs is None:
                Xs = self.originals
            for mani, X in zip(self, Xs):
                mani.update_base(X)
            if is_registered:
                self.last_parametrization().originals[0].zero_()

    def __getitem__(self, idx):
        return self.manifolds.__getitem__(idx)

    def __len__(self):
        return self.manifolds.__len__()

    def __iter__(self):
        return self.manifolds.__iter__()

    def __dir__(self):
        return self.manifolds.__dir__()