# -*- coding: utf-8 -*-
"""
A base class module for dataset fetcher   
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'

import os
import tarfile
import numpy as np
try:
    import cPickle as pickle
except ImportError:
    import pickle

from main.util.dataset import URLFetcher, awarize, get_temp_folder
from main.util.dataset import LabeledDatum, LabeledSetManager, Registrator
from main.util.dataset import MultiRegistrator


def get_cifar10_repositories():
    """Holds cifar 10 rep."""
    return ["http://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"]

def get_ls_name():
    return "cifar10_ls"

def get_ts_name():
    return "cifar10_ts"

def fetch_cifar10(dataset_folder):
    """
    Fetch, write, load the cifar10 dataset

    Parameters
    ----------
    dataset_folder : directory
        The directory in which to dump/load the dataset

    Return
    ------
    TODO
    """
    repositories = get_cifar10_repositories()
    storage_manager = None  #  TODO
    layout_manager = LabeledSetManager()
    ls_registrator = Registrator(storage_manager, dataset_folder, 
                                 get_ls_name(), layout_manager)
    ts_registrator = Registrator(storage_manager, dataset_folder,
                                 get_ts_name(), layout_manager)
    registrator = MultiRegistrator([ls_registrator, ts_registrator], "cifar10")

    fetcher = Cifar10Fetcher(repositories, registrator, layout_manager, True)
    return fetcher.fetch()

def unpickle(file_):
    dict_ = None
    with open(file_, 'rb') as f_:
        dict_ = pickle.load(f_)
    return dict_

class Cifar10Fetcher(URLFetcher):
    """
    ==============
    Cifar10Fetcher
    ==============
    A :class:`URLFetcher` for the Cifar10 BD. 

    Data format
    -----------
    The data are expected to be archived in a tar.gz file with the layout
    specified at the original dataset site (see 'Reference') (December 2014)

    Reference
    ---------
    See http://www.cs.toronto.edu/~kriz/cifar.html for information
    about the dataset
    """
    def __init__(self, repositories, multi_registrator, layout, is_binary=True):
        URLFetcher.__init__(self, repositories, multi_registrator, is_binary)
        self._layout_manager = layout

    def _untar(self, tar, folder):
        # Collecting Ls/Ts set file names
        members = tar.getmembers()
        ls_files = [""]*5
        ts_file = None
        labels = None
        for member in members:
            if member.name.find("data_batch_") > 0:
                ls_files[member.name[-1]] = os.path.join(folder, member.name)
            if member.name.endswith("test_batch"):
                ts_file = os.path.join(folder, member.name)
            if member.name.endswith("batches.meta"):
                labels = os.path.join(folder, member.name)

        # Extracting the files
        tar.extractall(folder)

        return ls_files, ts_file, labels

    def _build_rgb(self, np_row):
        red = np_row[0:1024].reshape((32,32))
        green = np_row[1024:2048].reshape((32,32))
        blue = np_row[2048:3072].reshape((32,32))
        return np.dstack((red, green, blue))

    def _process_batch(self, batch_file):
        batch_dict = unpickle(batch_file)
        X = batch_dict["data"]
        labels = batch_dict["labels"]
        for r in xrange(X.shape[0]):
            np_img = self._build_rgb(X[r])
            self._register(LabeledDatum(np_img, labels[r]))


    def _process_and_store(self, tempfile):
        # Untar the file
        with get_temp_folder() as temp_folder, tarfile.open(tempfile) as tar:
            # Untaring
            ls_files, ts_file, labels_file = self._untar(tar, temp_folder)
            # Getting the labels
            label_dict = unpickle(labels_file)
            # Setting the dictionary in the layout manager
            self._layout_manager.set_label_dict(label_dict)

            registrator = self._get_registrator()

            # Processing the ls files
            registrator.switch(get_ls_name())
            for ls_file in ls_files:
                self._process_batch(ls_file)

            # Processing the ts files
            registrator.switch(get_ts_name())
            self._process_batch(ts_file)




    def load(self):
        registrator = self._get_registrator()

        # Learning set
        registrator.switch(get_ls_name())
        dataset = URLFetcher.load(self)
        ls = awarize(dataset)

        # Testing set
        registrator.switch(get_ts_name())
        dataset = URLFetcher.load(self)
        ts = awarize(dataset)

        return ls, ts




