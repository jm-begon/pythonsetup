# -*- coding: utf-8 -*-
"""
test triple and square
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'

import nose
from main.bbb.square import square, Power
from main.bbb.triple import triple

from main.bbb._square import square as square2
from main.bbb._triple import triple as triple2

def check_square(x):
    """Test square function"""
    nose.tools.assert_equal(square(x), x**2)

def test_square():
    for i in range(3):
        yield check_square, i


def test_power():
    """Test :class:`Power`"""
    power = Power(3)
    nose.tools.assert_equal(power(3), 27)
    nose.tools.assert_equal(power.get_set_power(4), 3)
    nose.tools.assert_equal(power(2), 16)


def test_triple():
    for i in range(4):
        yield check_triple, i


def check_triple(x):
    """Test triple function"""
    nose.tools.assert_equal(triple(x), x*3)


def test_triple2():
    nose.tools.assert_equal(triple2(102), 102*3)

def test_square2():
    nose.tools.assert_equal(square2(102), 102**2)
