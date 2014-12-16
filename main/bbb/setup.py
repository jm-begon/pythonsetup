# -*- coding: utf-8 -*-
"""
setup script
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'


import os

import numpy
from numpy.distutils.misc_util import Configuration


def configuration(parent_package="", top_path=None):

    config = Configuration("bbb", parent_package, top_path)
    
    config.add_extension("_square",
    					 sources=["_square.c"],
    					 include_dirs=[numpy.get_include()],
    					 extra_compile_args=["-O3"])

    config.add_extension("_triple",
    					 sources=["_triple.c"],
    					 include_dirs=[numpy.get_include()],
    					 extra_compile_args=["-O3"])


    config.add_subpackage('test')

    return config

if __name__ == "__main__":
    from numpy.distutils.core import setup
    setup(**configuration().todict())
