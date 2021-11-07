#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ======================================================================================================================== #
# Project  : Natural Language Recommendation                                                                               #
# Version  : 0.1.0                                                                                                         #
# File     : \job.py                                                                                                       #
# Language : Python 3.7.11                                                                                                 #
# ------------------------------------------------------------------------------------------------------------------------ #
# Author   : John James                                                                                                    #
# Company  : nov8.ai                                                                                                       #
# Email    : john.james@nov8.ai                                                                                            #
# URL      : https://github.com/john-james-sf/nlr                                                                          #
# ------------------------------------------------------------------------------------------------------------------------ #
# Created  : Sunday, November 7th 2021, 1:59:08 am                                                                         #
# Modified : Sunday, November 7th 2021, 12:31:32 pm                                                                        #
# Modifier : John James (john.james@nov8.ai)                                                                               #
# ------------------------------------------------------------------------------------------------------------------------ #
# License  : BSD 3-clause "New" or "Revised" License                                                                       #
# Copyright: (c) 2021 nov8.ai                                                                                              #
# ======================================================================================================================== #
from datetime import datetime
import logging
import multiprocessing as mp
from .project import Project
# ------------------------------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)


class Director:

    def __init__(self):
        self.name = self.__class__.__name__
        self._projects = []

    def _get_projects(self):
        logger.info("Inside {}".format(self.__class__.__name__))
        project = Project(5)
        project.load_jobs()
        self._projects.append(project)

    def get_projects(self):
        if not self._projects:
            self._get_projects()
        return self._projects

    def set_projects(self, projects):
        self._projects = projects

    def print_projects(self):
        for project in self._projects:
            print(project.results)
