# -*- coding: utf-8 -*-
"""
A base class module for dataset fetcher   
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'

import logging
from cifarfetcher import fetch_cifar10

if __name__ == "__main__":
    folder = "/home/jmbegon/jmbegon/testcifar/"
    logger_name = "cifar"

    # create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    # 'application' code
    logger.debug('debug message')
    logger.info('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')

    ls, ts = fetch_cifar10(folder, logger_name)

    print "Learning Set length :", len(ls)
    print "Testing Set length :", len(ts)

    img0, lab0 = ls[0]
    print "Shape and label :", img0.shape, lab0

    img0, lab0 = ts[0]
    print "Shape and label :", img0.shape, lab0
    