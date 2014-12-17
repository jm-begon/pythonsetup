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

from pythonsetup.util.dataset import LabeledSetFetcher, NumpyStorageManager


def get_cifar10_repositories():
    """Holds cifar 10 rep."""
    return ["http://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"]

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
    fetcher = Cifar10Fetcher(repositories, dataset_folder)
    return fetcher.fetch()



def _unpickle(file_):
    dict_ = None
    print "File :"; file_.__class__, file_
    try:
        with open(file_, 'rb') as f_:
            dict_ = pickle.load(f_)
    except TypeError:
        dict_ = pickle.load(file_)
    return dict_


class CifarImgGenerator:

    def __init__(self, batch_files):
        self._batches = batch_files
        self._current = None

    def _build_rgb(self, np_row):
        red = np_row[0:1024].reshape((32,32))
        green = np_row[1024:2048].reshape((32,32))
        blue = np_row[2048:3072].reshape((32,32))
        return np.dstack((red, green, blue))


    def __iter__(self):
        for batch in self._batches:
            batch_dict = _unpickle(batch)
            X = batch_dict["data"]
            labels = batch_dict["labels"]
            for r in xrange(X.shape[0]):
                X_ = self._build_rgb(X[r])
                y_ = labels[r]
                yield X_, y_



class CifarExtractor:

    def extract(self, cifar_file, callback_func):
        # Untar the file
        with tarfile.open(fileobj=cifar_file) as tar:
            # Untaring
            ls_files, ts_file, labels_file = self._untar(tar)
            # Getting the labels 
            label_list = _unpickle(labels_file)["label_names"]
            label_dict = dict()
            for i, label in enumerate(label_list):
                label_dict[i] = label

            # Calling back
            ls = CifarImgGenerator(ls_files)
            ts = CifarImgGenerator([ts_file])

            callback_func(ls, ts, label_dict)

    def _untar(self, tar):
        # Collecting Ls/Ts set file names
        members = tar.getmembers()
        ls_files = [""]*5
        ts_file = None
        labels = None
        for member in members:
            if member.name.find("data_batch_") > 0:
                index = int(member.name[-1]) - 1
                ls_files[index] = tar.extractfile(member.name)
            if member.name.endswith("test_batch"):
                ts_file = tar.extractfile(member.name)
            if member.name.endswith("batches.meta"):
                labels = tar.extractfile(member.name)

        return ls_files, ts_file, labels


class Cifar10Fetcher(LabeledSetFetcher):
    """
    ==============
    Cifar10Fetcher
    ==============
    A :class:`LabeledSetFetcher` for the Cifar10 BD. 

    Data format
    -----------
    The data are expected to be archived in a tar.gz file with the layout
    specified at the original dataset site (see 'Reference') (December 2014)

    Reference
    ---------
    See http://www.cs.toronto.edu/~kriz/cifar.html for information
    about the dataset
    """
    def __init__(self, repositories, base_folder, is_binary=True):
        LabeledSetFetcher.__init__(self, repositories, base_folder, 
                                   "cifar10_ls", "cifar10_ts", 
                                   NumpyStorageManager(), is_binary)


    def _process_and_store(self, tempfile):
        print "File downloaded"
        extractor = CifarExtractor()
        extractor.extract(tempfile, self._callback)





