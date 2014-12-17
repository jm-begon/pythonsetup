# -*- coding: utf-8 -*-
"""
A base class module for dataset fetcher   
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'

from .cifarfetcher import fetch_cifar10

if __name__ == "__main__":
    folder = "/home/jmbegon/jmbegon/testcifar/"

    ls, ts = fetch_cifar10(folder)

    print "Learning Set length :", len(ls)
    print "Testing Set length :", len(ts)

    img0, lab0 = ls[0]
    print "Shape and label :", img0.shape, lab0

    img0, lab0 = ts[0]
    print "Shape and label :", img0.shape, lab0
    