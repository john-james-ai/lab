#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ======================================================================================================================== #
# Project  : Natural Language Recommendation                                                                               #
# Version  : 0.1.0                                                                                                         #
# File     : \worker.py                                                                                                    #
# Language : Python 3.7.11                                                                                                 #
# ------------------------------------------------------------------------------------------------------------------------ #
# Author   : John James                                                                                                    #
# Company  : nov8.ai                                                                                                       #
# Email    : john.james@nov8.ai                                                                                            #
# URL      : https://github.com/john-james-sf/nlr                                                                          #
# ------------------------------------------------------------------------------------------------------------------------ #
# Created  : Sunday, November 7th 2021, 1:52:54 am                                                                         #
# Modified : Sunday, November 7th 2021, 1:57:20 am                                                                         #
# Modifier : John James (john.james@nov8.ai)                                                                               #
# ------------------------------------------------------------------------------------------------------------------------ #
# License  : BSD 3-clause "New" or "Revised" License                                                                       #
# Copyright: (c) 2021 nov8.ai                                                                                              #
# ======================================================================================================================== #
from datetime import datetime
import os
import logging
import logging.config
import logging.handlers
import multiprocessing as mp

# ------------------------------------------------------------------------------------------------------------------------ #


class Worker:

    def __init__(self, job, config):
        self.job = job
        self.config = config
        self.run()

    def run(self):
        logging.config.dictConfig(self.config)
        logger = logging.getLogger(self.job.name)
        logger.info(self.job.start)
        result = self.job.run()
        logger.info(self.job.complete)

# ------------------------------------------------------------------------------------------------------------------------ #


class QueueLogHandler:
    """
    A simple handler for logging events. It runs in the listener process and
    dispatches events to loggers based on the name in the received record,
    which then get dispatched, by the logging system, to the handlers
    configured for those loggers.
    """

    def handle(self, record):
        if record.name == "root":
            logger = logging.getLogger()
        else:
            logger = logging.getLogger(record.name)

        if logger.isEnabledFor(record.levelno):
            # The process name is transformed just to show that it's the listener
            # doing the logging to files and console
            record.processName = '%s (for %s)' % (
                current_process().name, record.processName)
            logger.handle(record)
# ------------------------------------------------------------------------------------------------------------------------ #


class Listener(mp.Process):

    def __init__(self, queue, stop_event, config):
        self.queue = queue
        self.stop_event = stop_event
        self.config = config
        self.run()

    def run(self):
        logging.config.dictConfig(self.config)
        listener = logging.handlers.QueueListener(
            self.queue, QueueLogHandler())
        listener.start()
        if os.name == 'posix':
            # On POSIX, the setup logger will have been configured in the
            # parent process, but should have been disabled following the
            # dictConfig call.
            # On Windows, since fork isn't used, the setup logger won't
            # exist in the child, so it would be created and the message
            # would appear - hence the "if posix" clause.
            logger = logging.getLogger('setup')
            logger.critical(
                'Should not appear, because of disabled logger ...')
        self.stop_event.wait()
        listener.stop()
