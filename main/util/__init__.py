# -*- coding: utf-8 -*-
"""
Package aaa
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'


from .indexer import Indexable, Sliceable
from .dataset import DataSet, Fetcher, URLFetcher, StorageManager
from .dataset import NumpyStorageManager, LayoutManager, Registrator, awarize
from .dataset import LabeledDataSet, LabeledDatum, LabeledEntry, TempFolder
from .dataset import LabeledStorageManager, LabeledSetManager, MultiRegistrator
from .dataset import get_temp_folder

__all__ = ["Indexable", "Sliceable", "DataSet", "Fetcher", "URLFetcher", 
           "StorageManager", "NumpyStorageManager", "LayoutManager", 
           "Registrator", "MultiRegistrator", "awarize", "LabeledDataSet", 
           "LabeledDatum", "LabeledEntry", "LabeledStorageManager", 
           "LabeledSetManager", "TempFolder", "get_temp_folder"]
