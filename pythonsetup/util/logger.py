# -*- coding: utf-8 -*-
"""
A helper module for logging progress
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'


import time


def format_duration(duration):
    """
    Format the duration expressed in seconds as string

    Parameters
    ----------
    duration : float
        a duration in seconds
    Return
    ------
    formated : str
        the given duration formated

    Example
    -------
    >>> days = 1
    >>> hours = 4
    >>> minutes = 52
    >>> seconds = 23
    >>> duration = seconds + 60*(minutes + 60*(hours + 24*days))
    >>> format_duration(duration)
    '1d 4h 52m 23s'
    """
    sec = duration % 60
    excess = int(duration) // 60  # minutes
    res = str(sec) + "s"
    if excess == 0:
        return res
    minutes = excess % 60
    excess = excess // 60  # hours
    res = str(minutes) + "m " + res
    if excess == 0:
        return res
    hour = excess % 24
    excess = excess // 24  # days
    res = str(hour) + "h " + res
    if excess == 0:
        return res
    res = str(excess)+"d " + res
    return res


def format_size(nb_bytes):
    """
    Format a size expressed in bytes as a string

    Parameters
    ----------
    nb_bytes : int
        the number of bytes

    Return
    ------
    formated : str
        the given number of bytes fromated

    Example
    -------
    >>> format_size(100)
    '100.0 bytes'
    >>> format_size(1000)
    '1.0 kB'
    >>> format_size(1000000)
    '1.0 MB'
    >>> format_size(1000000000)
    '1.0 GB'
    >>> format_size(1000000000000)
    '1.0 TB'
    >>> format_size(1000000000000000000)
    '1000000.0 TB'

    """
    for x in ['bytes', 'kB', 'MB', 'GB']:
        if nb_bytes < 1000.0:
            return "%3.1f %s" % (nb_bytes, x)
        nb_bytes /= 1000.0
    return "%3.1f %s" % (nb_bytes, 'TB')


class ProgressableTask:
    """
    ================
    ProgressableTask
    ================
    A :class:`ProgressableTask` is a task whose progression can n steps.
    Once the progression hits the max, the task status goes
    from `ProgressableTask.RUNNING` to `ProgressableTask.DONE`

    Note
    ----
    A task with 10 steps comprises 11 states : 0 (nothing is done yet)
    1-9 and 10 (task completed). In order to complete a task of 10 steps,
    the update must reach "10", that is, all the 10 steps have been completed

    Class attributes
    ----------------
    nb_tasks : int
        The number of already created tasks. Beware that this is not
        thread-safe

    Class constants
    ---------------
    RUNNING : int
        State of a running task
    DONE : int
        State of a completed task

    Instance attributes
    -------------------
    id : int
        The id of the task
    name : str
        The name of the task

    Constructor parameters
    ----------------------
    nb_steps : int
        The number of step before completion
    name : str
        The name of the task
    """
    nb_tasks = 0

    RUNNING = 1
    DONE = 2
    UNFINISHED = 3

    def __init__(self, nb_steps, name=None):

        
        self.id = ProgressableTask.nb_tasks
        ProgressableTask.nb_tasks += 1

        if name is None:
            name = "Unnamed_task."+str(self.id)
        self.name = name

        self._nb_steps = nb_steps
        self._progress = 0
        self._last_reset = 0
        self._status = ProgressableTask.RUNNING
        self._end_time = None
        self._start_time = time.time()

    def get_nb_steps(self):
        """
        Returns
        -------
        nb_steps : int
            The number of steps required by the task
        """
        return self._nb_steps

    def ___len__(self):
        steps =  self.get_nb_steps()
        if steps is None:
            raise TypeError("Unbounded task")
        return steps

    def update(self, progress):
        """
        Update progress (if task is running)

        Parameters
        ----------
        progress : int
            the new progression score

        Return
        ------
        done : boolean
            True if the task is completed, False otherwise
        """
        if self._status == ProgressableTask.DONE:
            return True
        self._progress = progress
        if self._nb_steps is None:
            return False
        if progress >= self._nb_steps:
            self._progress = self._nb_steps
            self.close()
            return True
        else:
            return False

    def increment(self, inc=1):
        """
        Increment the progress by a given number

        Parameters
        ----------
        inc : int (Default : 1)
            The progress increment

        Return
        ------
        done : boolean
            True if the task is completed, False otherwise
        """
        return self.update(self.get_progress()+inc)

    def close(self, finished=True):
        """
        Ends the task

        Parameters
        ----------
        finished : boolean (Default : True)
            Whether the task has finished its excution correctly
        """
        if finished:
            self._status = ProgressableTask.DONE
        else:
            self._status = ProgressableTask.UNFINISHED
        self._end_time = time.time()

    def reset(self):
        """
        Reset the last progress counter. See method:`get_last_progress`
        """
        self._last_reset = self._progress

    def get_last_progress(self):
        """
        Return
        ------
        progress_ratio : float
            The relative progress since the last reset
        """
        if self._nb_steps is None:
            return 0
        return (float(self._progress - self._last_reset)/self._nb_steps)


    def duration(self):
        """
        Return
        ------
        duration : float
            the duration of taks in seconds (up to now if still running,
            up to completion if completed)
        """
        if self._status == ProgressableTask.DONE:
            return self._end_time - self._start_time
        else:
            return time.time() - self._start_time

    def get_progress(self):
        return self._progress

    def is_completed(self):
        return self._status == ProgressableTask.DONE


class Formater:
    """
    ========
    Formater
    ========
    A :class:`Formater` format progresses as string

    Constructor parameters
    ----------------------
    format_func : callable (Default : str)
        A function to format progresses
    """

    def __init__(self, format_func=str, format_duration=format_duration):
        self._format_duration = format_duration
        self._format_func = format_func

    def format_task(self, task):
        return "Task " + str(task.id) +" '" + task.name + "' : "

    def format_progress(self, task):
        progress = task.get_progress()
        try:
            nb_steps = len(task)
            return self._format_func(progress)+"/"+self._format_func(nb_steps)
        except TypeError:
            return self._format_func(progress)



    def _format_nb_steps(self, task):
        str_nb_steps = "????"
        try:
            str_nb_steps = self._format_func(len(task))
        except TypeError:
            pass
        return str_nb_steps

    def format_creation(self, task):
        str_nb_steps = self._format_nb_steps(task)
        logging_message =  (self.format_task(task) +
                           "Creation " + " (" + str_nb_steps + " steps)")
        return logging_message


    def format_end(self, task):
        duration = self._format_duration(task.duration())
        str_nb_steps = self._format_nb_steps(task)
        if task.is_completed():
            logging_msg = (self.format_task(task)+
                           "Completion of the " +
                           str_nb_steps +
                           " step(s) in " + duration)
        else:
            logging_msg = (self.format_task(task)+
                           "Interruption after " +
                           self.format_progress(task)+
                           " step(s) in " + duration)
        return logging_msg


def discard(msg, *args, **kwargs):
    return


class CompositeGenerator():

    def __init__(self, generator, inc=1):
        self.generator = generator
        self.inc = inc

    def __len__(self):
        return len(self.generator)

    def __iter__(self):
        for elem in self.generator:
            yield self.inc, elem
    

def log_iteration(composite_generator, name=None, log_func=discard, 
                  formater=Formater(), log_ratio=0.01):
    length = None
    try:
        length = len(composite_generator)
    except TypeError:
        pass
    task = ProgressableTask(length, name)
    
    try:
        # Log the start of the task
        log_func(formater.format_creation(task))
        # Running the decorated generator
        for inc, elem in composite_generator:
            # log the iterations of the task
            if not task.increment(inc):
                # Task is still in progress
                # Logging the message if necessary
                perc_prog = task.get_last_progress()
                if perc_prog >= log_ratio:
                    task.reset()
                    log_func(formater.format_progress(task))
            # Yield the element
            yield elem
        task.close(True)
    except:
        task.close(False)
    finally:
        # Log the end of the task
        log_func(formater.format_end(task))


def log_loop(generator, name=None, log_func=discard, 
             formater=Formater(), log_ratio=0.01):
    return log_iteration(CompositeGenerator(generator), name, log_func,
                         formater, log_ratio)


def log_transfer(generator, chunck_size, name=None, log_func=discard,
                 formater=Formater(format_func=format_size), log_ratio=0.01):
    return log_iteration(CompositeGenerator(generator, chunck_size), name, 
                         log_func, formater, log_ratio)

