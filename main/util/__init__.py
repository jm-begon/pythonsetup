# -*- coding: utf-8 -*-
"""
Package aaa
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'


from .indexer import Indexable, Sliceable
from .dataset import DataSet, Fetcher, URLFetcher, LabeledSetFetcher
from .dataset import StorageManager, NumpyStorageManager, LayoutManager
from .dataset import LabeledDataSet, TempFolder, LabeledStorageManager
from .dataset import Registrator, LabeledSetManager, get_temp_folder, awarize

__all__ = ["Indexable", "Sliceable", "DataSet", "Fetcher", "URLFetcher", 
           "LabeledSetFetcher", "StorageManager", "NumpyStorageManager", 
           "LayoutManager", "Registrator", "awarize", "LabeledDataSet", 
           "LabeledStorageManager", "LabeledSetManager", "TempFolder", 
           "get_temp_folder"]
