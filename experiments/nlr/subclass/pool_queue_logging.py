#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ======================================================================================================================== #
# Project  : Natural Language Recommendation                                                                               #
# Version  : 0.1.0                                                                                                         #
# File     : \pool_queue_logging.py                                                                                        #
# Language : Python 3.7.11                                                                                                 #
# ------------------------------------------------------------------------------------------------------------------------ #
# Author   : John James                                                                                                    #
# Company  : nov8.ai                                                                                                       #
# Email    : john.james@nov8.ai                                                                                            #
# URL      : https://github.com/john-james-sf/nlr                                                                          #
# ------------------------------------------------------------------------------------------------------------------------ #
# Created  : Sunday, November 7th 2021, 1:43:45 pm                                                                         #
# Modified : Sunday, November 7th 2021, 2:02:45 pm                                                                         #
# Modifier : John James (john.james@nov8.ai)                                                                               #
# ------------------------------------------------------------------------------------------------------------------------ #
# License  : BSD 3-clause "New" or "Revised" License                                                                       #
# Copyright: (c) 2021 nov8.ai                                                                                              #
# ======================================================================================================================== #
# %%
import logging
import logging.handlers
import multiprocessing
import multiprocessing.pool

from random import choice, random
import time


class ProcessLogger(multiprocessing.Process):
    _global_process_logger = None

    def __init__(self):
        super().__init__()
        self.queue = multiprocessing.Queue(-1)

    @classmethod
    def get_global_logger(cls):
        if cls._global_process_logger is not None:
            return cls._global_process_logger
        raise Exception("No global process logger exists.")

    @classmethod
    def create_global_logger(cls):
        cls._global_process_logger = ProcessLogger()
        return cls._global_process_logger

    @staticmethod
    def configure():
        root = logging.getLogger()
        h = logging.FileHandler('log_pool_queue.log', 'a')
        f = logging.Formatter(
            '%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')
        h.setFormatter(f)
        root.addHandler(h)

    def stop(self):
        self.queue.put_nowait(None)

    def run(self):
        self.configure()
        while True:
            try:
                record = self.queue.get()
                if record is None:
                    break
                logger = logging.getLogger(record.name)
                logger.handle(record)
            except Exception:
                import sys
                import traceback
                print('Whoops! Problem:', file=sys.stderr)
                traceback.print_exc(file=sys.stderr)

    # def new_process(self, target, args=[], kwargs={}):
    #     return ProcessWithLogging(self, target, args, kwargs)


def configure_new_process(log_process_queue):
    h = logging.handlers.QueueHandler(log_process_queue)
    root = logging.getLogger()
    root.addHandler(h)
    root.setLevel(logging.DEBUG)


class ProcessWithLogging(multiprocessing.Process):
    def __init__(self, target, args=[], kwargs={}, log_process=None):
        super().__init__()
        self.target = target
        self.args = args
        self.kwargs = kwargs
        if log_process is None:
            log_process = ProcessLogger.get_global_logger()
        self.log_process_queue = log_process.queue

    def run(self):
        configure_new_process(self.log_process_queue)
        self.target(*self.args, **self.kwargs)


class PoolWithLogging(multiprocessing.pool.Pool):
    def __init__(self, processes=None, context=None, log_process=None):
        if log_process is None:
            log_process = ProcessLogger.get_global_logger()
        super().__init__(processes=processes, initializer=configure_new_process,
                         initargs=(log_process.queue,), context=context)


LEVELS = [logging.DEBUG, logging.INFO,
          logging.WARNING, logging.ERROR, logging.CRITICAL]
LOGGERS = ['a.b.c', 'd.e.f']
MESSAGES = [
    'Random message #1',
    'Random message #2',
    'Random message #3',
]


def worker_process(param=None):
    name = multiprocessing.current_process().name
    print('Worker started: %s' % name)
    for i in range(10):
        time.sleep(random())
        logger = logging.getLogger(choice(LOGGERS))
        level = choice(LEVELS)
        message = choice(MESSAGES)
        message = message + " processing # {}".format(param)
        logger.log(level, message)
    print('Worker finished: {}, param: {}'.format(name, param))
    return param


def main():
    process_logger = ProcessLogger.create_global_logger()
    process_logger.start()

    workers = []
    # for i in range(10):
    #     worker = ProcessWithLogging(worker_process)
    #     workers.append(worker)
    #     worker.start()
    # for w in workers:
    #     w.join()

    with PoolWithLogging(processes=12) as pool:
        # print(pool.map(worker_process, range(8)))

        r = [pool.apply_async(
            func=worker_process, args=(i)) for i in range(10)]

    print(r)
    process_logger.stop()
    process_logger.join()


if __name__ == '__main__':
    main()
# %%
