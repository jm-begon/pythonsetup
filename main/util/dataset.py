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
from contextlib import contextmanager, closing
import string

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



class Fetcher:

    __metaclass__ = ABCMeta
    
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

    def __init__(self, repositories, registrator, is_binary=True):
        self.__repositories = repositories
        self.__registrator = registrator
        self.__is_binary = is_binary
    
    def get_repositories(self):
        return self.__repositories

    def is_binary_file(self):
        return self.__is_binary

    def already_done(self):
        return self.__registrator.already_dumped()

    def _register(self, datum):
        self.__registrator.register(datum)

    def fetch_and_store(self):
        repositories = self.get_repositories()
        # Create a temp file to download the dataset in
        mode = "w+b" if self.is_binary_file() else "w+t"
        with tempfile.TemporaryFile(mode=mode) as temp:
            found = False
            for repository in repositories:
                try:
                    with closing(urlopen(repository)) as url:
                        # We have our url, we need to dump it into a file
                        shutil.copyfileobj(url, temp)
                        with self.__registrator:
                            self._process_and_store(temp)
                    found = True
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
            if not found:
                raise last_except

    def _get_storage_manager(self):
        return self.__registrator.get_storage_manager()

    def _get_registrator(self):
        return self.__registrator


    @abstractmethod
    def _process_and_store(self, tempfile):
        pass

    def load(self):
        entries = self.__registrator.get_entries()
        loader = self._get_storage_manager()
        return DataSet(entries, loader)


class StorageManager:
    """

    save datum, return entry <->  load entry

    filepath : no extension !!
    """

    def __init__(self):
        pass

    def load(self, entry):
        return pickle.load(entry)

    def _prepare(self, filepath):
        folder, _ = os.path.split(filepath)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
    
    def save(self, datum, filepath):
        self._prepare(filepath)
        with open(filepath) as f:
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

    @abstractmethod
    def get_storage_manager(self):
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
            self.set_entries(pickle.load(self._metafile))
        else:
            self.set_entries([])


    def register(self, datum):
        name = self._layout_manager.name(datum)
        filepath = os.path.join(self._dataset_folder, name)
        entry = self.__storage_manager.save(datum, filepath)
        self.add_entries(entry)


    def close(self):
        with open(self._metafile) as f:
            pickle.dump(self._entries, f, pickle.HIGHEST_PROTOCOL)


class MultiRegistrator(Registrator):


    def __init__(self, registrators, dataset_name):
        Registrator.__init__(self, registrators[0].get_storage_manager(), 
                             dataset_name)

        self._current = registrators[0]
        self._registrators = dict()
        for registrator in registrators:
            self._registrators[registrator.get_dataset_name()] = registrator

    def __iter__(self):
        for registrator in self._registrators.itervalues():
            yield registrator 


    def already_dumped(self):
        for registrator in self:
            if not registrator.already_dumped():
                return False
        return True

    def register(self, datum):
        self._current.register(datum)

    def switch(self, dataset_name):
        previous = self._current.get_dataset_name()
        self._current = self._registrators[dataset_name]
        return previous

    def open(self):
        try:
            for registrator in self:
                registrator.open()
        except:
            self.close()

    def _unsafe_close(self, registrators):
        if len(registrators) == 0:
            return
        reg = registrators.pop()
        try:
            reg.close()
        finally:
            self._unsafe_close(registrators)

    def close(self):
        # Copy the list
        registrators = [x for x in self]
        self._unsafe_close(registrators)




def awarize(dataset):
    entries = dataset.seed
    loader = dataset.loader
    cls = dataset.__class__
    return LabeledDataSet(entries, loader, cls)

class LabeledDataSet(DataSet):
    """
    entries : list of :class:`LabeledEntry`
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


class LabeledDatum:
    def __init__(self, actual_datum, label):
        self.datum = actual_datum
        self.label = label

    def __str__(self):
        return "("+str(self.label)+", "+str(self.datum)+")"

    def __iter__(self):
        yield self.datum
        yield self.label


class LabeledEntry:

    def __init__(self, filepath, label):
        self.filepath = filepath
        self.label = label

    def __str__(self):
        return "("+str(self.label)+", "+str(self.filepath)+")"

    def __iter__(self):
        yield self.filepath
        yield self.label


class LabeledStorageManager(StorageManager):

    def __init__(self, decorated):
        self._decorated = decorated

    def get_loader(self):
        return self._decorated

    def load(self, entry):
        """
        entry : :class:`LabeledEntry`
        """
        filepath, label = entry
        return self._decorated.load(filepath), label

    def save(self, datum, filepath):
        """
        datum : :class:`LabeledDatum`
        Return
        ------
        entry : class:`LabeledEntry`
        """
        _, label = datum
        self._decorated.save(datum, filepath)
        return LabeledEntry(filepath, label)

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
                self._dict[key] = [c for c in val if c in get_valid_chars()]

    def translate(self, label):
        if self._dict is not None:
            label = self._dict.get(label, label)
        return str(label)

    def format_name(self, label_str, count):
        return label_str+"_"+count

    def name(self, datum):
        """
        datum : :class:`LabeledDatum`
        """
        _, label = datum
        label_str = self.translate(label)
        count = self._history.get(label_str, 0)
        # Create unique name
        os.path.join(label_str, self.format_name(label_str, count))
        # Update the counter
        count += 1
        self._history[label_str] = count


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

