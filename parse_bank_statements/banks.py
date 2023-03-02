import logging, traceback, csv
from parse_bank_statements import dates

logger = logging.getLogger('PBS.banks')
logger.setLevel(logging.DEBUG)

help = """
AREA boundaries: (top-y, left-x, bottom-y, right-x).
COLUMNS separators (x-positions).
To find them out for the specific PDF column format of a given bank's statements, use e.g. gimp, mode typogr.points.
"""


def amount_sparkasse(str_in):
    '''Convert string to float (money amount)'''

    moneyStr = str_in.strip().replace('.', '').replace(',', '.')

    money = 0
    for contrib in moneyStr.split('\n'):
        if contrib == '':
            return None
        try:
            moneyVal = float(contrib[:-1])
            if contrib[-1] == '-':
                moneyVal = -moneyVal
            money += moneyVal
        except:
            traceback.print_exc()
            money = None

    return money


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



class sskm:


    label   = 'sskm'
    rootDir = '/afs/ipp-garching.mpg.de/home/g/git/attach/sskm/gk'
#    rootDir = '/home/gio/bank/sskm/gk'
    pdfArea    = (139.5, 60, 707.5, 573)
    pdfColumns = (116.4, 163.3, 360, 465.4)
    ibanStr = 'ubiger-ID:'

    def csv2tras(self, fcsv):
        '''Split a statement into a list of transaction dictionaries'''

        logger.debug(fcsv)
        tra_list = csv2transactions(fcsv)
        transactions = []
        for transa in tra_list:
            if len(transa) == 4:
                transa.append('')
            tra = {}
            tra['date'], tra['date_currency'], tra['descr'], amount_out, amount_in = transa
            if self.ibanStr in tra['descr']:
                descr, tra['iban'] = tra['descr'].split(self.ibanStr, 1)
                tra['iban'] = tra['iban'].strip()
                tra['descr'] = descr.strip()
            else:
                tra['iban'] = None
            descr = tra['descr'] # parse a bit more
            if descr.count('\n') > 1:
                tra['type'], tra['user'], tra['descr'] = descr.split('\n', 2)
            elif descr.count('\n') > 0:
                tra['type'], tra['descr'] = descr.split('\n', 1)
            tra['descr'] = tra['descr'].strip()
            minus = self.amount(amount_in)
            if minus is not None:
                tra['amount'] = minus
            else:
                tra['amount'] = self.amount(amount_out)

            transactions.append(tra)

        return transactions

    def amount(self, str_in):
        '''Convert string to float (money amount)'''

        return(amount_sparkasse(str_in))


class sskm2:

    label = 'sskm2'
    rootDir = '/afs/ipp-garching.mpg.de/home/g/git/attach/sskm/gk'
#    rootDir = '/home/gio/bank/sskm/gk'
    pdfArea    = (139.5, 60, 750, 573)
    pdfColumns = (122.1, 362.8, 470)
    ibanStr = 'ubiger-ID:'

    def csv2tras(self, fcsv):

        '''Split a statement into a list of transaction dictionaries'''

        logger.debug(fcsv)
        tra_list = csv2transactions(fcsv, saldo_pos=1)
        transactions = []
        for transa in tra_list:
            tra = {}
            tra['date'], tra['descr'], amount_out, amount_in = transa
            if self.ibanStr in tra['descr']:
                descr, tra['iban'] = tra['descr'].split(self.ibanStr, 1)
                tra['iban'] = tra['iban'].strip()
                tra['descr'] = descr.strip()
            else:
                tra['iban'] = None
            descr = tra['descr'] # parse a bit more
            if descr.count('\n') > 1:
                tra['type'], tra['user'], tra['descr'] = descr.split('\n', 2)
            elif descr.count('\n') > 0:
                tra['type'], tra['descr'] = descr.split('\n', 1)
            tra['descr'] = tra['descr'].strip()
            minus = self.amount(amount_in)
            if minus is not None:
                tra['amount'] = minus
            else:
                tra['amount'] = self.amount(amount_out)
            transactions.append(tra)

        return transactions

    def amount(self, str_in):
        '''Convert string to float (money amount)'''

        return(amount_sparkasse(str_in))


class diba:

    label   = 'diba'
    rootDir = '/afs/ipp-garching.mpg.de/home/g/git/attach/lucia/diba'
#    rootDir = '/home/gio/bank/diba'
    pdfArea    = (190, 67, 765, 568)
    pdfColumns = (131, 507)
    mandatStr   = 'Mandat:'
    referenzStr = 'Referenz:'

    def csv2tras(self, fcsv):
        '''Split a statement into a list of transaction dictionaries'''

        logger.debug(fcsv)
        tra_list = csv2transactions(fcsv, saldo_str='Saldo', saldo_pos=1)
        transactions = []
        for jtra, transa in enumerate(tra_list):
            if jtra%2 == 0:
                tra = {}
                tra['date'], type_user, amount_eur = transa
                tra['type'], tra['user'] = type_user.split(' ', 1)
                tra['amount'] = self.amount(amount_eur)
            else:
                tra['date_currency'], descr, _ = transa
                if descr:
                    if self.mandatStr in descr:
                        tra['mandat'] = descr.split(self.mandatStr, 1)[1].strip()
                    elif self.referenzStr in descr:
                        tra['reference'] = descr.split(self.referenzStr, 1)[1].strip()
                transactions.append(tra)

        return transactions

    def amount(self, str_in):
        '''Convert string to float (money amount)'''

        str_in = str_in.strip().replace('.', '').replace(',', '.')
        if str_in == '':
            return None
        try:
            money = float(str_in)
        except:
            traceback.print_exc()
            money = None
        return money


class visa:

    label   = 'visa'
    rootDir = '/afs/ipp-garching.mpg.de/home/g/git/attach/sskm/kk'
#    rootDir = '/home/gio/bank/sskm/kk'
    pdfArea    = (300, 37, 750, 590)
    pdfColumns = (80, 120, 280, 360, 450, 530)

    def csv2tras(self, fcsv):
        '''Split a statement into a list of transaction dictionaries)'''

        logger.debug(fcsv)
        tra_list = csv2transactions(fcsv, saldo_str='Saldo', saldo_pos=2)
        transactions = []
        for transa in tra_list:
            tra = {}
            tra['date'], tra['date_currency'], tra['descr'], tra['currency'], tra['amount_raw'], \
                tra['exchange'], amount_eur = transa
            tra['amount'] = self.amount(amount_eur)
            transactions.append(tra)

        return transactions

    def amount(self, str_in):
        '''Convert string to float (money amount)'''

        return(amount_sparkasse(str_in))


class kskmse:

    label   = 'kskmse'
    rootDir = '/afs/ipp-garching.mpg.de/home/g/git/attach/lucia/kskmse'
#    rootDir = '/home/gio/bank/kskmse'
    pdfArea    = (139.5, 60, 707.5, 573)
    pdfColumns = (116.4, 163.3, 360, 465.4)
    ibanStr = 'ubiger-ID:'

    def csv2tras(self, fcsv):
        '''Split a statement into a list of transaction dictionaries'''

        logger.debug(fcsv)
        tra_list = csv2transactions(fcsv)
        transactions = []
        for transa in tra_list:
            if len(transa) == 4:
                transa.append('')
            tra = {}
            tra['date'], tra['date_currency'], tra['descr'], amount_out, amount_in = transa
            if self.ibanStr in tra['descr']:
                descr, tra['iban'] = tra['descr'].split(self.ibanStr, 1)
                tra['iban'] = tra['iban'].strip()
                tra['descr'] = descr.strip()
            else:
                tra['iban'] = None
            descr = tra['descr'] # parse a bit more
            if descr.count('\n') > 1:
                tra['type'], tra['user'], tra['descr'] = descr.split('\n', 2)
            elif descr.count('\n') > 0:
                tra['type'], tra['descr'] = descr.split('\n', 1)
            tra['descr'] = tra['descr'].strip()
            minus = self.amount(amount_in)
            if minus is not None:
                tra['amount'] = minus
            else:
                tra['amount'] = self.amount(amount_out)

            transactions.append(tra)

        return transactions

    def amount(self, str_in):

        return(amount_sparkasse(str_in))
