#!/usr/bin/env python
# coding: utf-8

"""Parse bank statements
"""

__author__  = 'Giovanni Tardini'
__version__ = '0.1.3'
__date__    = '18.01.2023'

import logging

fmt = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')
hnd = logging.StreamHandler()
hnd.setFormatter(fmt)
hnd.setLevel(level=logging.INFO)
logger = logging.getLogger('parse-bank-init')
logger.addHandler(hnd)
logger.setLevel(logging.INFO)
logger.propagate = False

from .parse_bank_statements import *

import encodings.utf_8
