#!/usr/bin/env python

import os, sys, csv # project tabula-py, requiring Java

help = """
AREA boundaries: (top-y, left-x, bottom-y, right-x).
COLUMNS separators (x-positions).
To find them out for the specific PDF column format of a given bank's statements, use e.g. gimp, mode typogr.points.
Define the PAGE END string in 'end_str'
"""

area = { \
    'sskm': (139.5, 60, 707.5, 573), \
    'ksk' : (139.5, 60, 707.5, 573), \
    'diba': (190, 67, 765, 568), \
    'visa': (300, 37, 750, 590) }

cols = { \
    'sskm': (116.4, 163.3, 360, 465.4), \
    'ksk' : (116.4, 163.3, 360, 465.4), \
    'diba': (131, 507), \
    'visa': (80, 120, 280, 360, 450, 530) }

def pdf2csv(fpdf, fcsv, bank):
    '''Convert a PDF statement into csv text format'''

    try:
        import tabula
    except:
        print('Module tabula-py not found, skipping PDF->csv')
        return ''

    if not os.path.isfile(fpdf):
        log = 'File %s not found\n' %fpdf
    else:
        if os.path.isfile(fcsv):
            log = ''
        else:
            tabula.convert_into(fpdf, fcsv, output_format="csv", pages="all", area=area[bank], columns=cols[bank], silent=True)
            log = 'Converting %s into %s\n' %(fpdf, fcsv)

    return log
