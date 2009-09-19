#!/usr/bin/python

# $Id: logger.py 84 2009-02-26 23:08:06Z fpletz $
# ----------------------------------------------------------------------------
# "THE MATE-WARE LICENSE"
# codec <codec@muc.ccc.de> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a mate in return.
# ----------------------------------------------------------------------------

import logging
import inspect
from logging import getLogger

from upay.config import config

fmt = '%(asctime)s %(levelname)s: %(name)s.%(func)s(): %(message)s'
logging.basicConfig(level=logging.INFO,
                    format=fmt,
                    datefmt='%m-%d %H:%M',
                    filename='/tmp/consumr.log',
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(fmt)
console.setFormatter(formatter)
getLogger().addHandler(console)

# automatic function invocation logs (decorator)
def flogger(logger):
    if config.getboolean('general', 'tracing'):
        def flogger_f(f):
            def ret(*args, **kwargs):
                logger.debug('invoked', func=f.func_name)
                retval = f(*args, **kwargs)
                logger.debug('returned "%s"' % str(retval),
                        func=f.func_name)
                return retval
            return ret
        return flogger_f
    else:
        def nologger(f):
            def ret(*args, **kwargs):
                return f(*args, **kwargs)
            return ret
        return nologger

oldLogger = logging.getLoggerClass()

class NullLogger(oldLogger):
    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def critical(self, *args, **kwargs):
        pass

    def exception(self, *args, **kwargs):
        pass

    def log(self, *args, **kwargs):
        pass


class MyLogger(oldLogger):
    def _extra_func(self, kwargs):
        if 'extra' not in kwargs:
            kwargs['extra'] = {}

        if 'func' in kwargs:
            kwargs['extra']['func'] = kwargs['func']
            del kwargs['func']
        else:
            kwargs['extra']['func'] = inspect.stack()[1][3]

        return kwargs
 
    def debug(self, *args, **kwargs):
        oldLogger.debug(self, *args, **self._extra_func(kwargs))

    def info(self, *args, **kwargs):
        oldLogger.info(self, *args, **self._extra_func(kwargs))

    def warning(self, *args, **kwargs):
        oldLogger.warning(self, *args, **self._extra_func(kwargs))

    def error(self, *args, **kwargs):
        oldLogger.error(self, *args, **self._extra_func(kwargs))

    def critical(self, *args, **kwargs):
        oldLogger.critical(self, *args, **self._extra_func(kwargs))

    def exception(self, *args, **kwargs):
        oldLogger.exception(self, *args, **self._extra_func(kwargs))

    def log(self, *args, **kwargs):
        oldLogger.log(self, *args, **self._extra_func(kwargs))

if config.getboolean('general', 'logging'):
    logging.setLoggerClass(MyLogger)
else:
    logging.setLoggerClass(NullLogger)

