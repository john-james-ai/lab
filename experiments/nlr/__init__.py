#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ======================================================================================================================== #
# Project  : Natural Language Recommendation                                                                               #
# Version  : 0.1.0                                                                                                         #
# File     : \__init__.py                                                                                                  #
# Language : Python 3.7.11                                                                                                 #
# ------------------------------------------------------------------------------------------------------------------------ #
# Author   : John James                                                                                                    #
# Company  : nov8.ai                                                                                                       #
# Email    : john.james@nov8.ai                                                                                            #
# URL      : https://github.com/john-james-sf/nlr                                                                          #
# ------------------------------------------------------------------------------------------------------------------------ #
# Created  : Sunday, November 7th 2021, 1:49:24 am                                                                         #
# Modified : Sunday, November 7th 2021, 6:01:37 am                                                                         #
# Modifier : John James (john.james@nov8.ai)                                                                               #
# ------------------------------------------------------------------------------------------------------------------------ #
# License  : BSD 3-clause "New" or "Revised" License                                                                       #
# Copyright: (c) 2021 nov8.ai                                                                                              #
# ======================================================================================================================== #

"""Top-level package for Cookie."""
import logging

__author__ = """John James"""
__email__ = 'john.james.sf@gmail.com'
__version__ = '0.1.0'

# ------------------------------------------------------------------------------------------------------------------------ #
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# ------------------------------------------------------------------------------------------------------------------------ #
LOG_FILEPATH = ".logs/debug.log"
LOG_FILEPATH_ERRORS = ".logs/error.log"


def get_queue_config(queue):
    return {
        'version': 1,
        'disable_existing_loggers': True,
        'handlers': {
            'queue': {
                'class': 'logging.handlers.QueueHandler',
                'queue': queue
            }
        },
        'root': {
            'handlers': ['queue'],
            'level': 'DEBUG'
        }
    }


config_main = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG'
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG'
    }
}

config_listener = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'detailed': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
        },
        'simple': {
            'class': 'logging.Formatter',
            'format': '%(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': LOG_FILEPATH,
            'mode': 'w',
            'formatter': 'detailed',
            'level': 'DEBUG'
        },
        'errors': {
            'class': 'logging.FileHandler',
            'filename': LOG_FILEPATH_ERRORS,
            'mode': 'w',
            'formatter': 'detailed',
            'level': 'ERROR'
        }
    },
    'root': {
        'handlers': ['console', 'file', 'errors'],
        'level': 'DEBUG'
    }
}
