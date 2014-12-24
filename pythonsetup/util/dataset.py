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
import string
import logging
from .indexer import Sliceable
from .logger import log_transfer

def get_valid_chars():
    return "-_.()%s%s" % (string.ascii_letters, string.digits)


class DataSet(Sliceable):
    """
    """
    def __init__(self, entries, loader):
        self.seeds = entries
        self.loader = loader

    def _get(self, index):
        return self.loader.load(self.seeds[index])

    def _slice(self, shallow_copy, slice_range):
        shallow_copy.seeds = self.seeds[slice_range]

    def __len__(self):
        return len(self.seeds)

    def get_loader(self):
        return self.loader

class Chunker:

    def __init__(self, url, chunk_size=8192):
        self._url = url
        self._response = None
        self._size = 0
        self._chunk_size = chunk_size

    def __enter__(self):
        self._response = urlopen(self._url)

    def __exit__(self, type, value, traceback):
        self._response.close()
        self._response = None

    def __len__(self):
        if self._response is None:
            raise TypeError("URL not opened yet")
        if self._size is None:
            try:
                self._size = int(self._response.info().getheader('Content-Length').strip())
            except AttributeError:
                raise TypeError("Cannot determine length")
        return self._size

    def __iter__(self):
        if self._response is None:
            raise StopIteration("URL not opened")
        while True:
            chunk = self._response.read(self._chunk_size)
            if not chunk:
                raise StopIteration()
            yield chunk

    def get_chunk_size(self):
        return self._chunk_size


class Fetcher:

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    
    def fetch(self):
        if not self.already_done():
            self.fetch_and_store()
        return self.load()

    @abstractmethod
    def already_done(self):
        pass

    @abstractmethod
    def fetch_and_store(self):
        pass

    @abstractmethod
    def load(self):
        pass





class URLFetcher(Fetcher):

    def __init__(self, repositories, dataset_name, is_binary=True, 
                 logger_name=__name__, chunk_size=8192):
        Fetcher.__init__(self)
        self.__repositories = repositories
        self.__is_binary = is_binary
        self.__chunk_size = chunk_size
        self.__name = dataset_name
        self.__logger = logging.getLogger(logger_name)
    
    def get_repositories(self):
        return self.__repositories

    def is_binary_file(self):
        return self.__is_binary


    def fetch_and_store(self):
        repositories = self.get_repositories()
        # Create a temp file to download the dataset in
        mode = "w+b" if self.is_binary_file() else "w+t"
        with tempfile.TemporaryFile(mode=mode) as temp:
            found = False
            for repository in repositories:
                try:
                    with Chunker(repository, self.__chunk_size) as chunker:
                        # We have our url, we need to dump it into a file
                        # Starting the actual download  
                        for chunk in log_transfer(chunker, 
                                                  chunker.get_chunk_size(),
                                                  "Downloading "+self.__name,
                                                  self.__logger.info):
                            temp.write(chunk)
                        
                        
                        # Reseting pointer at the start of the file
                        temp.seek(0)

                        # Processing the file
                        self._process_and_store(temp)
                    found = True
                    break
                except HTTPError as exception:
                    self.__logger.error("Could not use repository '"+
                                        str(repository)+"'. Error code is '"+
                                        exception.code+"' ("+
                                        exception.message+")") 
                    last_except = exception
                    if exception.code not in [403, 404]:
                        raise exception
                except URLError as exception:
                    self.__logger.error("Could not use repository '"+
                                        str(repository)+"' ("+
                                        exception.message+")")
                    last_except = exception
            # Checking we have indeed received a dataset
            if not found:
                raise last_except

    @abstractmethod
    def _process_and_store(self, tempfile):
        pass

    @abstractmethod
    def load(self):
        pass

class LabeledSetFetcher(URLFetcher):
    """
    ==============
    LabeledSetFetcher
    ==============
    A :class:`URLFetcher` for 

    Data format
    -----------
    The data are expected to be archived in a tar.gz file with the layout
    specified at the original dataset site (see 'Reference') (December 2014)

    """
    def __init__(self, repositories, base_folder, ls_name, ts_name, 
                 base_storage_manager, is_binary=True):
        URLFetcher.__init__(self, repositories, is_binary)
        self._layout_manager = LabeledSetManager()
        self._base_storage_manager = base_storage_manager
        self._storage_manager = LabeledStorageManager(base_storage_manager)
        self._ls_register = Registrator(self._storage_manager, base_folder,
                                        ls_name, self._layout_manager)
        self._ts_register = Registrator(self._storage_manager, base_folder,
                                        ts_name, self._layout_manager)

    def _callback(self, ls, ts, label_dict):
        self._layout_manager.set_label_dict(label_dict)
        with self._ls_register:
            for obj, label in ls:
                self._ls_register.register((obj, label))

        with self._ts_register:
            for obj, label in ts:
                self._ts_register.register((obj, label))

    def already_done(self):
        return (self._ls_register.already_dumped() and 
                self._ts_register.already_dumped())


    def load(self):
        ls = LabeledDataSet(self._ls_register.get_entries(),
                            self._storage_manager)
        ts = LabeledDataSet(self._ts_register.get_entries(),
                            self._storage_manager)
        return ls, ts

    @abstractmethod
    def _process_and_store(self, tempfile):
        pass


class StorageManager:
    """

    save datum, return entry <->  load entry

    filepath : no extension !!
    """

    def __init__(self):
        pass

    def load(self, entry):
        with open(entry) as f:
            tmp = pickle.load(f)
        return tmp

    def _prepare(self, filepath):
        folder, _ = os.path.split(filepath)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
    
    def save(self, datum, filepath):
        self._prepare(filepath)
        with open(filepath, "wb") as f:
            pickle.dump(datum, f, pickle.HIGHEST_PROTOCOL)
        return filepath

class NumpyStorageManager(StorageManager):

    def __init__(self):
        StorageManager.__init__(self)

    def load(self, entry):
        return np.load(entry)

    def save(self, datum, filepath):
        self._prepare(filepath)
        np.save(filepath, datum)
        if isinstance(filepath, str):
            filepath += ".npy"
        return filepath



class LayoutManager:
    """

    .
    | -- 0
    | -- 1
    | -- 2
    + -- 3
    """

    def __init__(self):
        self._count = 0

    def name(self, datum):
        """
        Return
        ------
        path : str
            The path to the datum. It is extensionless and may contain
            a folder hierarchy
        """
        n = self._count
        self._count += 1
        return n

class AbstractRegistrator:

    __metaclass__ = ABCMeta

    def __init__(self, storage_manager, dataset_name):
        self.__storage_manager = storage_manager
        self.__name = dataset_name
        self.__entries = None

    @abstractmethod
    def already_dumped(self):
        pass

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def register(self, datum):
        pass

    @abstractmethod
    def close(self):
        pass

    def get_dataset_name(self):
        return self.__name


    def add_entries(self, entry):
        if self.__entries is None:
            self.get_entries()
        self.__entries.append(entry)

    def get_entries(self):
        if self.__entries is None:
            self.open() 
        return self.__entries

    def set_entries(self, entries):
        self.__entries = entries


    def get_storage_manager(self):
        return self.__storage_manager

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()
        return False

class Registrator(AbstractRegistrator):

    ENTRIES_FILE = "0meta"

    def __init__(self, storage_manager, base_folder, dataset_name,
                 layout_manager=LayoutManager()):

        AbstractRegistrator.__init__(self, storage_manager, dataset_name)

        self._layout_manager = layout_manager
        self._base_folder = base_folder
        self._dataset_name = dataset_name
        self._dataset_folder = os.path.join(base_folder, dataset_name)
        self._metafile = os.path.join(self._dataset_folder, 
                                      Registrator.ENTRIES_FILE)
        

    def already_dumped(self):
        return os.path.exists(self._metafile)

    def open(self):
        if not os.path.exists(self._dataset_folder):
            os.mkdir(self._dataset_folder)
        if os.path.exists(self._metafile):
            with open(self._metafile) as f:
                self.set_entries(pickle.load(f))
        else:
            self.set_entries([])


    def register(self, datum):
        name = self._layout_manager.name(datum)
        filepath = os.path.join(self._dataset_folder, name)
        entry = self.get_storage_manager().save(datum, filepath)
        self.add_entries(entry)


    def close(self):
        with open(self._metafile, "wb") as f:
            pickle.dump(self.get_entries(), f, pickle.HIGHEST_PROTOCOL)



def awarize(dataset):
    entries = dataset.seed
    loader = dataset.loader
    cls = dataset.__class__
    return LabeledDataSet(entries, loader, cls)

class LabeledDataSet(DataSet):
    """
    entries : list of pairs (filepath, label)
    """

    def __init__(self, entries, labeled_loader, base_dataset_class=DataSet):
        DataSet.__init__(self, entries, labeled_loader)
        self._bdc = base_dataset_class

    def get_raw_data(self):
        X = [x for x, _ in self.seeds]
        labeled_loader = self.get_loader()
        loader = labeled_loader.get_loader()
        return self._bdc(X, loader)

    def get_labels(self):
        return [y for _, y in self.seeds]

    def unzip(self):
        X = self.get_raw_data()
        y = self.get_labels()
        return X, y

    def __iter__(self):
        yield self.get_raw_data()
        yield self.get_labels()



class LabeledStorageManager(StorageManager):

    def __init__(self, decorated):
        self._decorated = decorated

    def get_loader(self):
        return self._decorated

    def load(self, entry):
        """
        entry : pair (filepath, label)
        """
        filepath, label = entry
        return self._decorated.load(filepath), label

    def save(self, datum, filepath):
        """
        datum : pair (actual_datum, label)
        Return
        ------
        entry : pair (filepath, label)
        """
        actual_datum, label = datum
        filepath = self._decorated.save(actual_datum, filepath)
        return (filepath, label)

class LabeledSetManager(LayoutManager):

    """
        .
        | -- label1
        |      | -- label1_0
        |      + -- label1_1
        + -- label2
               | -- label2_0
               + -- label2_1
    """

    def __init__(self, label_dict=None):
        LayoutManager.__init__(self)
        self._history = dict()
        self._dict = None
        self.set_label_dict(label_dict)

    def set_label_dict(self, label_dict):
        self._dict = None
        if label_dict is not None:
            self._dict = dict()
            for key, val in label_dict.iteritems():
                tmp = ""
                for c in val:
                    if c in get_valid_chars():
                        tmp += c
                self._dict[key] = tmp

    def translate(self, label):
        if self._dict is not None:
            label = self._dict.get(label, label)
        return str(label)

    def format_name(self, label_str, count):
        return label_str+"_"+str(count)

    def name(self, datum):
        """
        datum : pair (acutal_datum, label)
        """
        _, label = datum
        label_str = self.translate(label)
        count = self._history.get(label_str, 0)
        # Create unique name
        name_ = os.path.join(label_str, self.format_name(label_str, count))
        # Update the counter
        count += 1
        self._history[label_str] = count
        return name_


def get_temp_folder(suffix="", prefix="tmp", dir=None):
    folder = tempfile.mkdtemp(suffix, prefix, dir)
    return TempFolder(folder)

class TempFolder:

    @classmethod
    def create_folder(cls):
        folder = tempfile.mkdtemp()
        return TempFolder(folder)


    def __init__(self, folder_path):
        self._folder = folder_path

    def open(self):
        if not os.path.exists(self._folder):
            #tempfile.mkdtemp(dir=self._folder)
            os.makedirs(self._folder)
        return self._folder

    def close(self):
        if os.path.exists(self._folder):
            shutil.rmtree(self._folder)

    def __enter__(self):
        self.open()
        return self._folder

    def __exit__(self, type, value, traceback):
        self.close()
        return False

