#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ======================================================================================================================== #
# Project  : Natural Language Recommendation                                                                               #
# Version  : 0.1.0                                                                                                         #
# File     : \projects.py                                                                                                  #
# Language : Python 3.7.11                                                                                                 #
# ------------------------------------------------------------------------------------------------------------------------ #
# Author   : John James                                                                                                    #
# Company  : nov8.ai                                                                                                       #
# Email    : john.james@nov8.ai                                                                                            #
# URL      : https://github.com/john-james-sf/nlr                                                                          #
# ------------------------------------------------------------------------------------------------------------------------ #
# Created  : Sunday, November 7th 2021, 2:13:12 am                                                                         #
# Modified : Sunday, November 7th 2021, 1:10:44 pm                                                                         #
# Modifier : John James (john.james@nov8.ai)                                                                               #
# ------------------------------------------------------------------------------------------------------------------------ #
# License  : BSD 3-clause "New" or "Revised" License                                                                       #
# Copyright: (c) 2021 nov8.ai                                                                                              #
# ======================================================================================================================== #
import logging
import logging.handlers
from datetime import datetime
import multiprocessing as mp
from random import choice, random, randint
from experiments.parallel.workers import worker
import time
# ------------------------------------------------------------------------------------------------------------------------ #


class Job:

    loggers = ['blue_log', 'red_log']
    levels = [logging.DEBUG, logging.INFO, logging.WARNING,
              logging.ERROR, logging.CRITICAL]

    def __init__(self, i):
        self.i = i
        self.name = mp.current_process().name

    def run(self):
        x = 0
        y = 0
        for i in range(randint(5, 20)):
            x += 1
            y += i ** 2
            logger = logging.getLogger(choice(Job.loggers))
            level = choice(Job.levels)
            message = 'I made %s last year' % (
                "${:,.2f}".format(randint(9999999, 99999999)))
            logger.log(level, message)
        logger.info('Worker %s processed job #%d  squaring up to %d for a sum of %d' %
                    (self.name, self.i, x, y))
        return {'process': self.name, 'job': self.i, 'x': x, 'y': y}


class Project:
    def __init__(self, n):
        self.name = self.__class__.__name__
        self.n = n
        self.jobs = None
        self.results = None

    def load_jobs(self):
        self.jobs = [Job(i) for i in range(self.n)]

    def compile_results(self, results):
        self.results = results
