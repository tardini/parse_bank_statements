#!/usr/bin/env python

import os, sys, csv # project tabula-py, requiring Java
import dates

help = """
AREA boundaries: (top-y, left-x, bottom-y, right-x).
COLUMNS separators (x-positions).
To find them out for the specific PDF column format of a given bank's statements, use e.g. gimp, mode typogr.points.
"""

area = { \
    'sskm' : (139.5, 60, 707.5, 573), \
    'sskm2': (139.5, 60, 750, 573), \
    'ksk'  : (139.5, 60, 707.5, 573), \
    'diba' : (190, 67, 765, 568), \
    'visa' : (300, 37, 750, 590) }

cols = { \
    'sskm' : (116.4, 163.3, 360, 465.4), \
    'sskm2': (122.1, 362.8, 470), \
    'ksk'  : (116.4, 163.3, 360, 465.4), \
    'diba' : (131, 507), \
    'visa' : (80, 120, 280, 360, 450, 530) }


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


def csv2transactions(fcsv, date_pos=0, saldo_pos=2, saldo_str='Kontostand'):

    transactions = []
    dates_index = []
    with open(fcsv, newline='') as csvfile:
        csvreader = csv.reader(csvfile, quotechar='"')
        for jline, line in enumerate(csvreader):
            csvDate = line[date_pos].strip()
            if dates.isdate(csvDate):
                dates_index.append(jline)
        if not(dates_index):
            return transactions
        firstDateLine = dates_index[0]
        lastDateLine  = dates_index[-1]

    with open(fcsv, newline='') as csvfile:
        csvreader = csv.reader(csvfile, quotechar='"')
        for jline, line in enumerate(csvreader):
            if jline < firstDateLine:
                continue
            csvDate = line[date_pos].strip()
            descr   = line[saldo_pos].strip()
            if jline in dates_index: # Line containing date
                if jline > firstDateLine:  # Not first date-line ever: close previous tra
                    transactions.append(tra)
                tra = [x.strip() for x in line] # Start a new tra
            else:
                if saldo_str in descr and jline > lastDateLine:
                    break
                if csvDate: # Not a date, not empty either
                    if jline > lastDateLine: # bottom, close csv
                        break
                    else:  # Out of statements table, ignore line
                        continue
                else:       # Empty first entry, append to previous strings
                    tra = [(tra[jpos] + '\n' + x).strip() for jpos, x in enumerate(line)]

    transactions.append(tra)

    return transactions


if __name__ == '__main__':

    fcsv = '%s/attach/sskm/gk/2021/Konto_131409-Auszug_2021_001.csv' %os.getenv('HOME')
    tras = csv2transactions(fcsv)
    for tra in tras:
        print(tra)
    print(fcsv)
