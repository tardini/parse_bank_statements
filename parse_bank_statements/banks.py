import logging
from datetime import datetime
import pandas as pd
import pdfplumber

logger = logging.getLogger('PBS.banks')

translate_header = {'Datum': 'date', 'Wert': 'date2', 'Erläuterung': 'descr',
                    'Betrag Soll EUR': 'amount in', 'Betrag Haben EUR': 'amount out',
                    'Betrag EUR': 'Amount', 'Buchung': 'date',
                    'Buchung / Verwendungszweck': 'descr', 'Betrag (EUR)': 'Amount',
                    'Beleg-': 'date', 'Eingang': 'date2',
                    'Angabe des Unternehmens /': 'descr',
                    'Währung': 'currency', 'Betrag': 'amount orig',
                    'Kurs': 'change', 'Betrag in': 'Amount'}
    
def isdate(s):
    s = s.strip().replace(' ','')
#    s = s.strip()
    for fmt in ("%d.%m.%Y", "%d.%m.%y"):
        try:
            datetime.strptime(s, fmt)
            return True
        except ValueError:
            pass
    return False


def to_numeric(df_col):
    def convert_one(s):
        s = s.strip()
        if not s:
            return 0.0
        s = (s.replace(".", "").replace(",", "."))  # German -> international comma

# trailing + or - sign
        if s.endswith("-"):
            s = "-" + s[:-1]
        elif s.endswith("+"):
            s = s[:-1]
        return float(s)

    return df_col.fillna("").str.split("\n").apply(
        lambda values: sum(convert_one(v) for v in values))


def get_word_pos(words, keyword):
    for word in words:
        if word['text'] == keyword:
            return word['x0'], word['bottom']
    return None


def print_all_words(page):
    words = page.extract_words()
    for word in words:
        print(word)


def get_row(page, keyword):
    words = page.extract_words(x_tolerance=2, keep_blank_chars=True)
    x0, y0 = get_word_pos(words, keyword)
    words_in_line = [word for word in words if abs(word['bottom'] - y0) < 1]
    row = [word['text'].strip() for word in words_in_line]
    return row, words_in_line[0]['x0'], words_in_line[0]['bottom']


def get_table_area(page, bank=''):

# Get all horizontal lines
    hlines = [l for l in page.lines if l['height'] == 0 and l["width"] > 20]

# Vertical extent
    if len(hlines) >= 2:
        line_up   = min(hlines, key=lambda l: l["top"])
        line_down = max(hlines, key=lambda l: l["top"])
        y_up   = line_up["top"]
        y_down = line_down["bottom"]
    elif len(hlines) == 1:
        y_up   = hlines[0]["top"]
        y_down = page.height
    else:
        return None

# Horizontal extent
    xmin = hlines[0]["x0"]
    xmax = hlines[0]["x1"]

    return [xmin, y_up, xmax, y_down]


class STATEMENT:


    def __init__(self, bank, fpdf):

        logger.info(fpdf)
        bank_name = bank.__class__.__name__
        logger.info(bank_name)
        settings = {key: val for key, val in bank.settings.items()}

        with pdfplumber.open(fpdf) as pdf:
            self.header, xh, yh = get_row(pdf.pages[0], bank.headerKeyword)
            logger.info(self.header)
            for jpage, page in enumerate(pdf.pages):
                margins = get_table_area(page)
                logger.debug('Page: %s, Auto margins: %s', jpage, margins)

                if bank_name in ('SSKM', 'KSKMSE'):
                    left_margin = xh
                    if left_margin is None:
                        break
                    margins = [left_margin-10, 0, page.width, page.height]
                else:
                    if margins is None: # No horizontal line
                        break
                    if bank_name in ('VISA', 'DIBA'):
                        margins = [margins[0], margins[1], page.width, page.height]
                logger.debug('Page: %s, New  margins: %s', jpage, margins)

                table_page = page.crop(margins)
                page_table = table_page.extract_table(settings)
                if jpage == 0:
                    self.table = page_table
                else:
                    if page_table is not None:
                        self.table += page_table

        self.stripTable(endString=bank.endString)
        if self.table is not None: # 0 transactions, only saldo
            self.balance = self.table[-1][-1]
            self.table = self.table[:-1] # Cut Saldo line


    def stripTable(self, endString='Neuer Saldo'):

# Remove empty rows or rows containing given keywords
        table = []
        for row in self.table:
            if (not row[0]) or (isdate(row[0])): # Skip row if first entry is not date nor blank
                concat = ''.join(row).strip()
                if concat:
                    if ('Zwischensumme' not in concat) and ('Übertrag' not in concat):
                        table.append(row)
            if endString in row:
                break

        date_rowIndex = [j for j, row in enumerate(table) if isdate(row[0])]
        
        if date_rowIndex:
# Cut table before first date
            self.table = table[date_rowIndex[0]:]
            self.date_rowIndex = [j for j, row in enumerate(self.table) if isdate(row[0])]
        else:
            self.table = None


    def to_df(self):

        blocks_d = {}
        if self.table is None: # PDF with o transactions, just Saldo
            columns = [translate_header[word] for word in self.header]
            self.df = pd.DataFrame(columns=columns)
        else:
            for jcol, word in enumerate(self.header):
                key = translate_header[word]
                blocks_d[key] = ['\n'.join(row[jcol] for row in self.table[start:end] if row[jcol])
                    for start, end in zip(self.date_rowIndex, self.date_rowIndex[1:] + [len(self.table)]) ]
            self.df = pd.DataFrame(blocks_d)
            
        if 'amount in' in self.df.columns:
            self.df['amount'] = to_numeric(self.df['amount in']) + to_numeric(self.df['amount out'])
        else:
            self.df['amount'] = to_numeric(self.df['Amount'])


def fromPDF(bank, fpdf):
    logger.debug(fpdf)
    stat = STATEMENT(bank, fpdf)
    stat.to_df()
    return stat.df

class SSKM:
    rootDir = 'sskm/gk'
    endString = None
    headerKeyword = 'Erläuterung'
    settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "text",
    }

class KSKMSE:
    rootDir = 'kskmse'
    endString = None
    headerKeyword = 'Erläuterung'
    settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "text",
    }

class DIBA:
    rootDir = 'diba'
    endString = 'Neuer Saldo'
    headerKeyword = 'Buchung / Verwendungszweck'
    settings = {
        "vertical_strategy": "explicit",
        "explicit_vertical_lines": [70, 131, 490, 555],
        "horizontal_strategy": "text",
    }

class VISA:
    rootDir = 'sskm/kk'
    endString='Neuer Saldo'
    headerKeyword = 'Währung'
    settings = {
        "vertical_strategy": "explicit",
        "explicit_vertical_lines": [40, 81, 120, 300, 360, 450, 515, 580],
        "horizontal_strategy": "text",
    }


if __name__ == '__main__':

    if not logger.handlers:
        fmt = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s: %(message)s', '%H:%M:%S')
        hnd = logging.StreamHandler()
        hnd.setFormatter(fmt)
        logger.addHandler(hnd)

    fpdf = '/shares/users/private/git/bank/sskm/gk/2026/Konto_0000131409-Auszug_2026_0001.PDF'
    fpdf = '/home/IPP-AD/git/Downloads/10_Oktober25.pdf'
    sskm = SSKM()
    df = fromPDF(sskm, fpdf)
    print(df['amount'])
