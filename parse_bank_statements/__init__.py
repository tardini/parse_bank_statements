#!/usr/bin/env python
# coding: utf-8

"""Parse bank statements
"""

import os, logging

__author__  = 'Giovanni Tardini'
__version__ = '0.2.0'
__date__    = '22.09.2026'


fmt = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s: %(message)s', '%H:%M:%S')
logger = logging.getLogger('PBS')
logger.setLevel(level=logging.INFO)
if not logger.handlers:
    hnd = logging.StreamHandler()
    hnd.setFormatter(fmt)
    logger.addHandler(hnd)

pbs_home = os.path.dirname(os.path.realpath(__file__))

logger.info('Using version %s', __version__)
logger.info('PBS home %s', pbs_home)

from .pbs_gui import *

import encodings.utf_8
