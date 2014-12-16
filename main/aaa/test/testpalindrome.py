# -*- coding: utf-8 -*-
"""
test palindrome
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'

import nose
from main.aaa import LP, LP_sparse 

def test_lp_caractere():
    """Test the longest palindrome of 'caractere'"""
    nose.tools.assert_equal(LP("caractere"), "carac")

def test_lps_caractere():
    """Test the longest palindrome of 'caractere' (sparse version)"""
    nose.tools.assert_equal(LP_sparse("caractere"), "carac")
    