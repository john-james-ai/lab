#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ======================================================================================================================== #
# Project  : Natural Language Recommendation                                                                               #
# Version  : 0.1.0                                                                                                         #
# File     : \pool_apply_with_log.py                                                                                       #
# Language : Python 3.7.11                                                                                                 #
# ------------------------------------------------------------------------------------------------------------------------ #
# Author   : John James                                                                                                    #
# Company  : nov8.ai                                                                                                       #
# Email    : john.james@nov8.ai                                                                                            #
# URL      : https://github.com/john-james-sf/nlr                                                                          #
# ------------------------------------------------------------------------------------------------------------------------ #
# Created  : Sunday, November 7th 2021, 2:53:52 pm                                                                         #
# Modified : Sunday, November 7th 2021, 2:56:22 pm                                                                         #
# Modifier : John James (john.james@nov8.ai)                                                                               #
# ------------------------------------------------------------------------------------------------------------------------ #
# License  : BSD 3-clause "New" or "Revised" License                                                                       #
# Copyright: (c) 2021 nov8.ai                                                                                              #
# ======================================================================================================================== #
# %%
import logging
import logging.handlers
import numpy as np
import time
import multiprocessing
import pandas as pd
log_file = 'log_file.log'


def listener_configurer():
    root = logging.getLogger()
    h = logging.FileHandler(log_file)
    f = logging.Formatter(
        '%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')
    h.setFormatter(f)
    root.addHandler(h)

# This is the listener process top-level loop: wait for logging events
# (LogRecords)on the queue and handle them, quit when you get a None for a
# LogRecord.


def listener_process(queue, configurer):
    configurer()
    while True:
        try:
            record = queue.get()
            if record is None:  # We send this as a sentinel to tell the listener to quit.
                break
            logger = logging.getLogger(record.name)
            # No level or filter logic applied - just do it!
            logger.handle(record)
        except Exception:
            import sys
            import traceback
            print('Whoops! Problem:', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)


def worker_configurer_old(queue):
    h = logging.handlers.QueueHandler(queue)  # Just the one handler needed
    root = logging.getLogger()
    root.addHandler(h)
    # send all messages, for demo; no other level or filter logic applied.
    root.setLevel(logging.DEBUG)


def worker_configurer(queue):
    root = logging.getLogger()
    # print(f'{root.handlers=}')
    if len(root.handlers) == 0:
        h = logging.handlers.QueueHandler(queue)
        root.addHandler(h)
        root.setLevel(logging.DEBUG)

# This is the worker process top-level loop, which just logs ten events with
# random intervening delays before terminating.
# The print messages are just so you know it's doing something!


def worker_function(sleep_time, name, queue, configurer):
    configurer(queue)
    start_message = 'Worker {} started and will now sleep for {}s'.format(
        name, sleep_time)
    logging.info(start_message)
    time.sleep(sleep_time)
    success_message = 'Worker {} has finished sleeping for {}s'.format(
        name, sleep_time)
    logging.info(success_message)


def main_with_pool():
    start_time = time.time()
    queue = multiprocessing.Manager().Queue(-1)
    listener = multiprocessing.Process(target=listener_process,
                                       args=(queue, listener_configurer))
    listener.start()
    pool = multiprocessing.Pool(processes=3)
    job_list = [np.random.randint(10) / 2 for i in range(10)]
    single_thread_time = np.sum(job_list)
    for i, sleep_time in enumerate(job_list):
        name = str(i)
        pool.apply_async(worker_function,
                         args=(sleep_time, name, queue, worker_configurer))

    pool.close()
    pool.join()
    queue.put_nowait(None)
    listener.join()
    end_time = time.time()
    print("Script execution time was {}s, but single-thread time was {}s".format(
        (end_time - start_time),
        single_thread_time
    ))


if __name__ == "__main__":
    main_with_pool()
# %%
