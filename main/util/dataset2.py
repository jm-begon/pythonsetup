# -*- coding: utf-8 -*-
"""
A base class module for dataset fetcher   
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'

from abc import ABCMeta, abstractmethod
import tempfile
import shutil
import os
import numpy as np
try:
    # Python 2
    from urllib2 import URLError, HTTPError
    from urllib2 import urlopen
except ImportError:
    # Python 3+
    from urllib.error import URLError, HTTPError
    from urllib.request import urlopen
try:
    import cPickle as pickle
except ImportError:
    import pickle

class DataSet:

    def __init__(self, X, y):
        self._X = X
        self._y = y

    def unzip(self):
        return self._X, self._y

class DataSetLoader:
    __metaclass__ = ABCMeta
    

    @abstractmethod
    def load(self):
        """
        Load the data at the specified path. The data are expected to be placed
        in the directory by the :meth:`write` method of the same class.


        Return
        ------
        data : <class specific>
            The loaded data 
        """
        pass

    

class DataSetFetcher:
    __metaclass__ = ABCMeta

    def __init__(self, folder):
        pass
    
    @abstractmethod
    def is_dumped(self):
        """
        Check whether the dataset has already been dumped

        Return
        ------
        isDumped : bool
            Whether the dataset has already been dumped at the given path
        """
        pass

    def fetch_and_dump(self, repositories):
        """
        Fetch and write the given data on the disk

        Parameters
        ----------
        repositories : iterable of <class-specific>
            A representations of the repositories where the dataset can be found.
        """
        pass

    @abstractmethod
    def clean(self):
        """
        Cleans the folder in which the data were written
        """
        pass

class LoaderFetcher(DataSetLoader, DataSetFetcher):
    __metaclass__ = ABCMeta
    pass

class Registrator:

    def __init__(self, folder, metafile):
        self._folder = folder
        self._filepath = os.path.join(folder, metafile)
        self.reset()

    def reset(self):
        self._obj_files = []
        self._labels = []

    def load(self):
        return pickle.load(self._filepath)

    def close(self):
        pickle.dump((self._labels, self._obj_files), 
                    self._filepath, pickle.HIGHEST_PROTOCOL)


    def register(self, obj, label):
        """
        Register an object-label pair for storing on disk

        Parameters
        ----------
        obj : <dataset-dependent>
            The object to store
        label : <dataset-dependent> (int or str usually)
            The label associated to the object
        """
        labelfolder = os.path.join(self._folder, label)
        if not os.path.exists(labelfolder):
            os.mkdir(labelfolder)
        self._do_register(obj, labelfolder)

    def _do_register(self, obj, filepath):
        if isinstance(obj, np.ndarray):
            np.dump(obj, filepath)
        else:
            pickel.dump(obj, filepath, pickle.HIGHEST_PROTOCOL)


    def __enter__(self):
        self.reset()
        return self

    def __exit__(self, type, value, traceback):
        self.close()


class HierarchizedLoaderFetcher(LoaderFetcher):
    """

    Hierarchy
    ---------
    base_folder
    +-- dataset_name
        | -- 0meta
        | -- label1
        |      | -- obj1
        |      + -- obj2
        + -- label2
               | -- obj1
               + -- obj2

    Constructor parameters
    ----------------------
    folder : directory
        The base folder in which to dump data
    """
    META_FILE = "0meta"
    
    def __init__(self, folder, registrator_class):
        self.__folder = folder
        filepath = os.path.join(folder, HierarchizedLoaderFetcher.META_FILE)
        self.__registrator = registrator_class(filepath)

    def get_base_folder(self):
        """Return the base folder"""
        return self.__folder

    def get_registrator(self):
        return self.__registrator

    def folder_view(self):
        """
        Return
        ------
        view : pair(obj_file_sequence, label_sequence)
            obj_file_sequence : sequence of files
                The files in which the objects have been stored
            label_sequence : sequence of labels
                The labels corresponding to the object of the same index
        """
        labels, obj_files = self.__registrator.load()
        return obj_files, labels


class SimpleLoader(DataSetLoader):
    """
    ============
    SimpleLoader
    ============
    A :class:`SimpleLoader` is a :class:`DataSetLoader` which uses
    the following simple folder hierarchy (from a given base folder):
    
    base_folder
    +-- dataset_name
        | -- label 1
        |      | -- img1
        |      + -- img2
        + -- label 2
               | -- img1
               + -- img2

    Note : The existence test will only check the presence of the dataset_name
    folder in the base_folder

    Dataset
    -------
    The dataset is, for now, a tuple (img_files, labels):
    img_files : sequence of str
        Each string represent the path to a file
    labels : sequence of int
        Each int is the label corresponding to the image file of the same index

    Constructor parameters
    ----------------------
    base_folder : directory
        The base folder in which to dump data
    dataset_name : str
        The name of the dataset
    """
    __metaclass__ = ABCMeta

    def __init__(self, base_folder, dataset_name):
        DataOrganizer.__init__(self, base_folder)
        self.__dataset_name = dataset_name

    def get_dataset_name(self):
        """Return the dataset name"""
        return self.__dataset_name

    def is_dumped(self):
        pass

    def load(self):
        pass

    def clean(self):
        folder = self.get_base_folder()
        dataset_name = self.get_dataset_name()
        dataset_folder = os.path.join(folder, dataset_name)
        if os.path.exists(dataset_folder):
            shutil.rmtree(dataset_folder) 





class SimpleFetcher(DataSetFetcher):
    """

    A :class:`SimpleFetcher` is a :class:`DataSetFetcher` which uses
    the following simple folder hierarchy (from a given base folder):
    
    base_folder
    +-- dataset_name
        | -- label 1
        |      | -- img1
        |      + -- img2
        + -- label 2
               | -- img1
               + -- img2
    """

class URLFetcher(SimpleFetcher):


class DataOrganizer:
    """
    =============
    DataOrganizer
    =============
    A :class:`DataOrganizer` write/load data to/from the disk.

    Writing phase
    -------------
    The writing phase expect data in some form (typically archive, specified by 
    the instance class) and write it to the disk in some organized fashion.

    Loading phase
    -------------
    The loading phase expect the on-disk data to be organized in the 
    aforementioned fashion and load it in some given form (typically a 
    learning/testing set, specified by the instance class).

    Constructor parameters
    ----------------------
    folder : directory
        The base folder in which to dump data
    """
    __metaclass__ = ABCMeta

    def __init__(self, folder):
        self.__folder = folder

    def get_base_folder(self):
        """Return the base folder"""
        return self.__base_folder


    @abstractmethod
    def write(self, data):
        """
        Write the given data on the disk

        Parameters
        ----------
        data : <class specific>
            The data to write on the disk
        """
        pass


    @abstractmethod
    def is_dumped(self):
        """
        Check whether the dataset has already been dumped

        Return
        ------
        isDumped : bool
            Whether the dataset has already been dumped at the given path
        """
        pass

    @abstractmethod
    def load(self):
        """
        Load the data at the specified path. The data are expected to be placed
        in the directory by the :meth:`write` method of the same class.


        Return
        ------
        data : <class specific>
            The loaded data 
        """
        pass

    @abstractmethod
    def clean(self):
        """
        Cleans the folder in which the data were written
        """
        pass





def fetch(data_organizer, repositories, binary=True):
    """
    Fetch, write and load the dataset.

    The fetch and write operations are omited if
        - there was no repository provided (repositories is None)
        - data_organizeranizer.is_dumped() == True

    Parameters
    ----------
    data_organizeranizer : :class:`DataOrganizer`
        The :class:`DataOrganizer` instance in charge of retrieving, writing
        and loading the dataset
    repositories : iterable of str or None
        The URLs where the dataset can be found. If None, directly loads
        the dataset from the dataset_folder.        
    binary : bool (Default : True)
        Whether the file retrieved is binary or not     
    """
    if (repositories is None or 
        not data_organizer.is_dumped()):
        # Not already dumped ? We dumped it
        # Create a temp file to download the dataset in
        mode = "w+b" if binary else "w+t"
        with tempfile.TemporaryFile(mode=mode) as temp:
            url = None
            for repository in repositories:
                try:
                    url = urlopen(repository)
                    # If we were able to open the url, we proceed
                    # with that file.
                    # If not, we have to try the next url
                    break
                except HTTPError as e:
                    # TODO : log
                    last_except = e
                    if e.code not in [403, 404]:
                        raise e
                except URLError as e:
                    # TODO : log e.reason
                    last_except = e
                # Checking we have indeed received a dataset
                if url is None:
                    raise last_except

            # We have our url, we need to dump it into a file
            shutil.copyfileobj(url, temp)

            # Writing data through de DataOrganizer
            data_organizer.write(temp, )

    # Loading the dataset
    return data_organizer.load()


class Fetcher:
    """
    =======
    Fetcher
    =======
    a :class:`Fetcher` adds withable capabilty to the :func:`fetch` function.
    Fetch, write and load the dataset.


    Constructor parameters
    ----------------------
    data_organizeranizer : :class:`DataOrganizer`
        The :class:`DataOrganizer` instance in charge of retrieving, writing
        and loading the dataset
    repositories : iterable of str or None
        The URLs where the dataset can be found. If None, directly loads
        the dataset from the dataset_folder.        
    dataset_folder : directory
        The directory in which to dump/load the dataset (See the corresponding 
            :class:`DataOrganizer` for more information)
    binary : bool (Default : True)
        Whether the file retrieved is binary or not   
    """

    def __init__(data_organizer, dataset_folder, repositories, binary=True,
                 always_clean=False):
        self._data_org = data_organizer
        self._folder = dataset_folder
        self._repo = repositories
        self._binary = binary
        self._always_clean = always_clean
        self._previous_dump = False

    def fetch(self):
        self._previous_dump = self._data_org.is_dumped()
        return fetch(self._data_org, self._folder, self._repo, self._binary)

    def __call__(self):
        return self.fetch()

    def __enter__(self):
        return self.fetch()

    def __exit__(self, type, value, traceback):
        if self._always_clean:
            self._data_org.clean()
        elif not self._previous_dump:
            self._data_org.clean()


class TempFolder:

    @classmethod
    def create_folder(cls):
        folder = tempfile.mkdtemp()
        return TempFolder(folder)


    def __init__(self, folder_path):
        self._folder = folder_path

    def open(self):
        if not os.path.exists(self._folder):
            tempfile.mkdtemp(dir=self._folder)

    def close(self):
        if os.path.exists(self._folder):
            shutil.rmtree(self._folder)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()







