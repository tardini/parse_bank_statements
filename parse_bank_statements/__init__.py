#!/usr/bin/env python
# coding: utf-8

"""Parse bank statements
"""

import os, logging

__author__  = 'Giovanni Tardini'
__version__ = '0.1.6'
__date__    = '02.03.2023'


fmt = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')
hnd = logging.StreamHandler()
hnd.setFormatter(fmt)
hnd.setLevel(level=logging.INFO)
logger = logging.getLogger('PBS')
logger.addHandler(hnd)
logger.setLevel(logging.INFO)
logger.propagate = False

pbs_home = os.path.dirname(os.path.realpath(__file__))

logger.info('Using version %s', __version__)
logger.info('PBS home %s', pbs_home)

from .pbs_gui import *

import encodings.utf_8
