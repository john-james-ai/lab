#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ======================================================================================================================== #
# Project  : Natural Language Recommendation                                                                               #
# Version  : 0.1.0                                                                                                         #
# File     : \__main__.py                                                                                                  #
# Language : Python 3.7.11                                                                                                 #
# ------------------------------------------------------------------------------------------------------------------------ #
# Author   : John James                                                                                                    #
# Company  : nov8.ai                                                                                                       #
# Email    : john.james@nov8.ai                                                                                            #
# URL      : https://github.com/john-james-sf/nlr                                                                          #
# ------------------------------------------------------------------------------------------------------------------------ #
# Created  : Sunday, November 7th 2021, 3:52:43 am                                                                         #
# Modified : Sunday, November 7th 2021, 2:15:10 pm                                                                         #
# Modifier : John James (john.james@nov8.ai)                                                                               #
# ------------------------------------------------------------------------------------------------------------------------ #
# License  : BSD 3-clause "New" or "Revised" License                                                                       #
# Copyright: (c) 2021 nov8.ai                                                                                              #
# ======================================================================================================================== #
# %%
import logging
import logging.config
import logging.handlers
import multiprocessing as mp
from random import choice
from experiments.nlr.package.director import Director
from experiments.nlr.package.project import Job

# ------------------------------------------------------------------------------------------------------------------------ #
LOG_FILEPATH = "logs/debug.log"
LOG_FILEPATH_ERRORS = "logs/error.log"
# ------------------------------------------------------------------------------------------------------------------------ #


class MyHandler:
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

        record.processName = '%s (for %s)' % (
            current_process().name, record.processName)
        logger.handle(record)


def listener_process(queue, configurer):
    logging.config.dictConfig(config)
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


def listener_process2(q, stop_event, config):
    """
    This could be done in the main process, but is just done in a separate
    process for illustrative purposes.

    This initialises logging according to the specified configuration,
    starts the listener and waits for the main process to signal completion
    via the event. The listener is then stopped, and the process exits.
    """
    logging.config.dictConfig(config)
    logger = logging.getLogger()
    logger.info("Inside the listener process.")
    listener = logging.handlers.QueueListener(q, MyHandler())
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


def worker_pool_init(config: dict):
    logging.config.dictConfig(config)


def worker_pool_process(job):
    logger = logging.getLogger(job.name)
    loggers = ['velvet', 'chaise']
    logger.info("We should be writing this to the queue.")
    result = job.run()
    return result


def execute_project(project, config_worker):

    pool = mp.Pool(processes=12, initializer=worker_pool_init,
                   initargs=config_worker)
    async_results = [pool.apply_async(
        func=worker_pool_process, args=(job)) for job in project.jobs]
    pool.close()
    pool.join()

    results = [async_result.get() for async_result in async_results]

    project.compile_results(results)

    return project


def work(director, config_worker):
    projects = director.get_projects()
    completed_projects = [execute_project(
        project, config_worker) for project in projects]
    director.set_projects(completed_projects)
    director.print_projects()
    return director


def main():
    queue = mp.Manager().Queue()

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

    # The worker process configuration is just a QueueHandler attached to the
    # root logger, which allows all messages to be sent to the queue.
    # We disable existing loggers to disable the "setup" logger used in the
    # parent process. This is needed on POSIX because the logger will
    # be there in the child following a fork().
    config_worker = {
        'version': 1,
        'disable_existing_loggers': True,
        'handlers': {
            'queue': {
                'class': 'logging.handlers.QueueHandler',
                'queue': queue,
                'level': 'DEBUG'
            }
        },
        'root': {
            'handlers': ['queue'],
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
                'level': 'DEBUG'
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': "log_debug.log",
                'mode': 'w',
                'formatter': 'detailed',
                'level': 'DEBUG'
            },
            'errors': {
                'class': 'logging.FileHandler',
                'filename': "log_errors.log",
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

    logging.config.dictConfig(config_main)
    logger = logging.getLogger('setup')
    logger.info('About to create listener ...')

    stop_event = mp.Event()
    lp = mp.Process(target=listener_process, name='listener',
                    args=(queue, config_listener))
    lp.start()

    director = Director()
    director = work(director, config_worker)

    logger.info('Telling listener to stop ...')
    # stop_event.set()
    # lp.join()
    queue.put_nowait(None)
    lp.join()
    logger.info('All done.')


if __name__ == '__main__':
    main()

    # %%
