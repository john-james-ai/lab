#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ======================================================================================================================== #
# Project  : Lab                                                                                                           #
# Version  : 0.1.0                                                                                                         #
# File     : \myhandler.py                                                                                                 #
# Language : Python 3.7.11                                                                                                 #
# ------------------------------------------------------------------------------------------------------------------------ #
# Author   : John James                                                                                                    #
# Company  : nov8.ai                                                                                                       #
# Email    : john.james@nov8.ai                                                                                            #
# URL      : https://github.com/john-james-sf/lab                                                                          #
# ------------------------------------------------------------------------------------------------------------------------ #
# Created  : Wednesday, October 27th 2021, 3:30:03 am                                                                      #
# Modified : Wednesday, October 27th 2021, 3:31:15 am                                                                      #
# Modifier : John James (john.james@nov8.ai)                                                                               #
# ------------------------------------------------------------------------------------------------------------------------ #
# License  : BSD 3-clause "New" or "Revised" License                                                                       #
# Copyright: (c) 2021 nov8.ai                                                                                              #
# ======================================================================================================================== #
import logging
from multiprocessing import current_process


class MyHandler(object):
    """
    A simple handler for logging events. It runs in the listener process and
    dispatches events to loggers based on the name in the received record,
    which then get dispatched, by the logging system, to the handlers
    configured for those loggers.
    """

    def handle(self, record):
        logger = logging.getLogger(record.name)
        # The process name is transformed just to show that it's the listener
        # doing the logging to files and console
        record.processName = '%s (for %s)' % (
            current_process().name, record.processName)
        logger.handle(record)
