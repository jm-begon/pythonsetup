# -*- coding: utf-8 -*-
"""
:mod:`Square` ...
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'

def square(x):
    """
    Return the x^2

    >>> square(4)
    16
    """
    return x**2

class Power:
    """
    =====
    Power
    =====
    A :class:`Power` raise numbers to some power

    Constructor parameters
    ----------------------
    n : int >= 0 (Default : 2)
        The power to which to raise numbers
    """

    def __init__(self, n=2):
        self._n = n

    def get_set_power(self, n=None):
        """
        Get and possibly set the power

        Parameters
        ----------
        n : int >= 0 or None (Default : None)
            The power to which to raise numbers
        Return
        ------
        n_prec : int >= 0
            The previous power
        """
        tmp = self._n
        if n is not None:
            self._n = n
        return tmp

    def __call__(self, x):
        return x**self._n
