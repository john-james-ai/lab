#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ======================================================================================================================== #
# Project  : Lab                                                                                                           #
# Version  : 0.1.0                                                                                                         #
# File     : \log.py                                                                                                       #
# Language : Python 3.7.11                                                                                                 #
# ------------------------------------------------------------------------------------------------------------------------ #
# Author   : John James                                                                                                    #
# Company  : nov8.ai                                                                                                       #
# Email    : john.james@nov8.ai                                                                                            #
# URL      : https://github.com/john-james-sf/lab                                                                          #
# ------------------------------------------------------------------------------------------------------------------------ #
# Created  : Monday, October 25th 2021, 10:52:48 pm                                                                        #
# Modified : Monday, November 1st 2021, 4:12:25 pm                                                                         #
# Modifier : John James (john.james@nov8.ai)                                                                               #
# ------------------------------------------------------------------------------------------------------------------------ #
# License  : BSD 3-clause "New" or "Revised" License                                                                       #
# Copyright: (c) 2021 nov8.ai                                                                                              #
# ======================================================================================================================== #
# %%
import math
import logging
import logging.handlers
import multiprocessing as mp

# Next two import lines for this demo only
from random import choice, random
import time
NUM_PROCESSORS = max(1, math.floor(mp.cpu_count() / 2))
LOGDIR = 'nlr/logs/'
#
# Because you'll want to define the logging configurations for listener and workers, the
# listener and worker process functions take a configurer parameter which is a callable
# for configuring logging for that process. These functions are also passed the queue,
# which they use for communication.
#
# In practice, you can configure the listener however you want, but note that in this
# simple example, the listener does not apply level or filter logic to received records.
# In practice, you would probably want to do this logic in the worker processes, to avoid
# sending events which would be filtered out between processes.
#
# The size of the rotated files is made small so you can see the results easily.


def listener_configurer():
    logfile = os.path.join(LOGDIR, 'listener.log')
    root = logging.getLogger()
    h = logging.handlers.TimedRotatingFileHandler(
        filename=logfile, when='midnight')
    root.setLevel(logging.DEBUG)
    i = logging.StreamHandler()
    f = logging.Formatter(
        '%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')
    h.setFormatter(f)
    i.setFormatter(f)
    root.addHandler(h)
    root.addHandler(i)

# This is the listener process top-level loop: wait for logging events
# (LogRecords)on the queue and handle them, quit when you get a None for a
# LogRecord.


def listener_process(queue, configurer):
    configurer()
    listener = logging.handlers.QueueListener(queue, MyHandler())
    listener.start()
    if os.name == 'posix':
        # On POSIX, the setup logger will have been configured in the
        # parent process, but should have been disabled following the
        # dictConfig call.
        # On Windows, since fork isn't used, the setup logger won't
        # exist in the child, so it would be created and the message
        # would appear - hence the "if posix" clause.
        logger = logging.getLogger('setup')
        logger.critical('Should not appear, because of disabled logger ...')
    stop_event.wait()
    listener.stop()

# Arrays used for random selections in this demo


LEVELS = [logging.DEBUG, logging.INFO, logging.WARNING,
          logging.ERROR, logging.CRITICAL]

LOGGERS = ['a.b.c', 'd.e.f']

MESSAGES = [
    'Random message #1',
    'Random message #2',
    'Random message #3',
]

# The worker configuration is done at the start of the worker process run.
# Note that on Windows you can't rely on fork semantics, so each process
# will run the logging configuration code when it starts.


def worker_configurer(queue):
    h = logging.handlers.QueueHandler(queue)  # Just the one handler needed
    root = logging.getLogger()
    root.addHandler(h)
    # send all messages, for demo; no other level or filter logic applied.
    root.setLevel(logging.DEBUG)

# This is the worker process top-level loop, which just logs ten events with
# random intervening delays before terminating.
# The print messages are just so you know it's doing something!


def worker_process(queue, configurer):
    configurer(queue)
    name = mp.current_process().name
    print('Worker started: %s' % name)
    for i in range(10):
        time.sleep(random())
        logger = logging.getLogger(choice(LOGGERS))
        level = choice(LEVELS)
        message = choice(MESSAGES)
        logger.log(level, message)
    print('Worker finished: %s' % name)

# Here's where the demo gets orchestrated. Create the queue, create and start
# the listener, create ten workers and start them, wait for them to finish,
# then send a None to the queue to tell the listener to finish.


def main():
    queue = mp.Manager().Queue(-1)
    listener = mp.Process(target=listener_process,
                          args=(queue, listener_configurer))
    listener.start()

    pool = mp.Pool(NUM_PROCESSORS)
    results = [pool.apply_async(func)]
    workers = []
    for i in range(10):
        worker = mp.Process(target=worker_process,
                            args=(queue, worker_configurer))
        workers.append(worker)
        worker.start()
    for w in workers:
        w.join()
    queue.put_nowait(None)
    listener.join()


if __name__ == '__main__':
    main()
# %%
