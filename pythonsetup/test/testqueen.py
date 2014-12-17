# -*- coding: utf-8 -*-
"""
test queen
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'

import nose
from main import nb_solutions 

def test_8_queens():
	"""Test the number of solutions for 8 queens"""
	nose.tools.assert_equal(nb_solutions(8), 92)
	