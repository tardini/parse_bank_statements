#!/usr/bin/env python

import os, sys, re, csv, webbrowser, datetime, logging
import tkinter as tk
import tkinter.scrolledtext as st
from tkinter import ttk
from tkinter import filedialog as tkfd
import numpy as np
import matplotlib.pylab as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
try:
    from . import pdf2csv, dates
except:
    import pdf2csv, dates

try:
    from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as nt2tk
except:
    from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg as nt2tk

fmt = logging.Formatter('%(name)s | %(levelname)s: %(message)s', '%H:%M:%S')
hnd = logging.StreamHandler()
hnd.setFormatter(fmt)
logger = logging.getLogger('PBS')
logger.addHandler(hnd)
logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.INFO)


iban_sskm = 'ubiger-ID:'
mand_diba = 'Mandat:'
ref_diba  = 'Referenz:'

end_str = {'sskm': 'Der Kon', 'ksk': 'Der Kon', 'diba': 'Kunden-In', 'visa': 'Sehr'}

info_text = \
'''PARSE BANK STATEMENTS

Author: Giovanni Tardini
Date: January 20th 2021

The app expects a directory structure of the type:
    <bank_statements_path>/2018
    <bank_statements_path>/2019
    <bank_statements_path>/2020
and the statements to be PDF.
Each bank has its <bank_statements_path>, this can be stored from the GUI and will be loaded on future usage.

PDF files are converted (una tantum) into CSV, based on the open source java-based package <a href="https://pypi.org/project/tabula-py">tabula-py</a>.

Supported banks: SSKM-Gyrokonto, Ing.Diba, SSKM-Visa-Kreditkarte, KSKMSE

Web docu at <a href="https://www2.ipp.mpg.de/~git/pbs/index.html">Statement Parser</a> page.

Repository <a href="https://github.com/tardini/parse_bank_statements.git">PBS github</a> 
'''

os.environ['BROWSER'] = '/usr/bin/google-chrome'


def formatHyperLink(text, message):

    url_tag_beg = '<a href="'
    url_tag_mid = '">'
    url_tag_end = '</a>'
    re_str = r'%s(?P<address>.*?)%s(?P<title>.*?)%s' %(url_tag_beg, url_tag_mid, url_tag_end)
    hyperlinkPattern = re.compile(re_str)

    start = 0
    text_str = ''
    for index, match in enumerate(hyperlinkPattern.finditer(message)):
        groups = match.groupdict()
        tag_id = 'URL%d' %index

        plain_text = message[start: match.start()]
        text.insert("end", plain_text)
        text_str += plain_text
        
        url_beg = len(text_str)
        url = groups['title']
        text.insert("end", url)
        text_str += url
        url_end = len(text_str)

        text.tag_add(tag_id, "1.0+%dc" %url_beg, "1.0+%dc" %url_end)
        text.tag_config(tag_id,
                        foreground="blue",
                        underline=1)
        text.tag_bind(tag_id,
                      "<Enter>",
                      lambda *a, **k: text.config(cursor="arrow"))
        text.tag_bind(tag_id,
                      "<Leave>",
                      lambda *a, **k: text.config(cursor="arrow"))
        text.tag_bind(tag_id,
                      "<Button-1>",
                      _openbrowser(groups['address']))

        start = match.end()


def _openbrowser(url):

    return lambda *args, **kwargs: webbrowser.open(url)


def plot_time(year_beg, year_end, amount, fig_time):


    fig_time.clf()
    fig_time.subplots_adjust(left=0.15, bottom=0.15, right=0.95, top=0.92, hspace=0)

    ax = fig_time.add_subplot(1, 1, 1)
    ax.set_xlabel('Year')
    ax.set_ylabel('Money \u20ac')
    xax = ax.get_xaxis()
    xax.grid(True, which='major')
    xax.set_major_locator(MaxNLocator(integer=True))
    if (max(amount) > 0) and (min(amount) >= 0):
        ax.set_ylim([0, 1.1*max(amount)])
    elif (min(amount) < 0) and (max(amount) <= 0):
        ax.set_ylim([1.1*min(amount), 0])
    ax.plot(range(year_beg, year_end+1), amount, color='g', marker='o')
    ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    ax.yaxis.major.formatter._useMathText = True
    fig_time.canvas.draw()


def amount_sskm(str_in):
    '''Convert string to float (money amount) for bank SSKM'''

    str_in = str_in.strip().replace('.', '').replace(',', '.')
    if str_in == '':
        return None
    try:
        money = float(str_in[:-1])
    except:
        logger.error('Error converting %s to float', str_in)
        money = None
    if str_in[-1] == '-':
        money = -money

    return money


def amount_diba(str_in):
    '''Convert string to float (money amount) for bank Ing.DIBA'''

    str_in = str_in.strip().replace('.', '').replace(',', '.')
    if str_in == '':
        return None
    try:
        money = float(str_in)
    except:
        logger.error('Error converting %s to float' %str_in)
        money = None
    return money


def csv2tras_sskm(fcsv):
    '''Split a statement into a list of transaction dictionaries (bank SSKM)'''

    logger.debug(fcsv)
    tra_list = pdf2csv.csv2transactions(fcsv)
    transactions = []
    for transa in tra_list:
        tra = {}
        tra['date'], tra['date_currency'], tra['descr'], amount_out, amount_in = transa
        if iban_sskm in tra['descr']:
            descr, tra['iban'] = tra['descr'].split(iban_sskm, 1)
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
        minus = amount_sskm(amount_in)
        if minus is not None:
            tra['amount'] = minus
        else:
            tra['amount'] = amount_sskm(amount_out)

        transactions.append(tra)
                
    return transactions


def csv2tras_sskm2(fcsv):

    '''Split a statement into a list of transaction dictionaries (bank SSKM)'''

    logger.debug(fcsv)
    tra_list = pdf2csv.csv2transactions(fcsv, saldo_pos=1)
    transactions = []
    for transa in tra_list:
        tra = {}
        tra['date'], tra['descr'], amount_out, amount_in = transa
        if iban_sskm in tra['descr']:
            descr, tra['iban'] = tra['descr'].split(iban_sskm, 1)
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
        minus = amount_sskm(amount_in)
        if minus is not None:
            tra['amount'] = minus
        else:
            tra['amount'] = amount_sskm(amount_out)
        transactions.append(tra)
                
    return transactions


def csv2tras_visa(fcsv):
    '''Split a statement into a list of transaction dictionaries (credit-card SSKM)'''

    logger.debug(fcsv)
    tra_list = pdf2csv.csv2transactions(fcsv, saldo_str='Saldo', saldo_pos=2)
    transactions = []
    for transa in tra_list:
        tra = {}
        tra['date'], tra['date_currency'], tra['descr'], tra['currency'], tra['amount_raw'], \
            tra['exchange'], amount_eur = transa
        tra['amount'] = amount_sskm(amount_eur)
        transactions.append(tra)

    return transactions


def csv2tras_diba(fcsv):
    '''Split a statement into a list of transaction dictionaries (bank Ing. DIBA)'''

    logger.debug(fcsv)
    tra_list = pdf2csv.csv2transactions(fcsv, saldo_str='Saldo', saldo_pos=1)
    transactions = []
    for jtra, transa in enumerate(tra_list):
        if jtra%2 == 0:
            tra = {}
            tra['date'], type_user, amount_eur = transa
            tra['type'], tra['user'] = type_user.split(' ', 1)
            tra['amount'] = amount_diba(amount_eur)
        else:
            tra['date_currency'], descr, _ = transa
            if descr:
                if mand_diba in descr:
                    tra['mandat'] = descr.split(mand_diba, 1)[1].strip()
                elif ref_diba in descr:
                    tra['reference'] = descr.split(ref_diba, 1)[1].strip()
            transactions.append(tra)

    return transactions


class pbs_gui:


    def __init__(self):


        pbsmain = tk.Tk()
        try:
            from . import pbs_style
        except:
            import pbs_style
        pbsmain.title('Bank-statement-parser')
        pbsmain.geometry('800x600')
        pbsmain.configure(background=pbs_style.frc)

# Menubar

        menubar  = tk.Menu(pbsmain)
        filemenu = tk.Menu(menubar, tearoff=0)

        filemenu.add_command(label="Parse statements", command=self.parse)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=sys.exit)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Info"    , command=self.info)

        menubar.add_cascade(label = "File", menu=filemenu)
        menubar.add_cascade(label = "Help", menu=helpmenu)

        menubar.configure(bg=pbs_style.tbc)
        pbsmain.config(menu = menubar)

        btframe     = ttk.Frame(pbsmain)
        bankframe   = ttk.Frame(pbsmain)
        wordframe   = ttk.Frame(pbsmain)
        dirframe    = ttk.Frame(pbsmain)
        year1frame  = ttk.Frame(pbsmain)
        year2frame  = ttk.Frame(pbsmain)
        amountframe = ttk.Frame(pbsmain)
        outframe    = ttk.Frame(pbsmain)
        
        for frame in btframe, bankframe, wordframe, dirframe, year1frame, year2frame, amountframe:
            frame.pack(side=tk.TOP, anchor=tk.W, pady=5)      

        outframe.pack(side=tk.TOP, anchor=tk.W, pady=5, expand=1, fill=tk.BOTH)
        txtframe = ttk.Frame(outframe, width=200)
        canframe = ttk.Frame(outframe, width=400)
        txtframe.pack(side=tk.LEFT, anchor=tk.W, fill=tk.Y)
        canframe.pack(side=tk.LEFT, anchor=tk.W, expand=1, fill=tk.BOTH)

        ttk.Button(btframe, text='Parse statements', command=self.parse, width=16).pack(side=tk.LEFT)

        ttk.Label(bankframe, text='Bank').pack(side=tk.LEFT)
        self.bank_wid = tk.StringVar()
        self.bank_wid.set('sskm')
        bank1 = ttk.Radiobutton(bankframe, text='SSKM', variable=self.bank_wid, value='sskm', command=self.sel)
        bank2 = ttk.Radiobutton(bankframe, text='DiBa', variable=self.bank_wid, value='diba', command=self.sel)
        bank3 = ttk.Radiobutton(bankframe, text='Visa', variable=self.bank_wid, value='visa', command=self.sel)
        bank4 = ttk.Radiobutton(bankframe, text='KSKMSE', variable=self.bank_wid, value='ksk', command=self.sel)
        for rb in bank1, bank2, bank3, bank4:
            rb.pack(side=tk.LEFT)

        ttk.Label(wordframe, text='Keyword').pack(side=tk.LEFT)
        self.word_wid = tk.Entry(wordframe, width=40)
        self.word_wid.insert(0, 'amazon')
        self.word_wid.pack(side=tk.LEFT)

        ttk.Label(dirframe, text='Start dir', width=12).pack(side=tk.LEFT)
        self.dir_wid = tk.Entry(dirframe, width=40)
        self.sel()
        self.dir_wid.pack(side=tk.LEFT)
        ttk.Button(dirframe, text='Save', command=self.save_dir).pack(side=tk.LEFT)

        ttk.Label(year1frame, text='Year start', width=12).pack(side=tk.LEFT)
        self.year_beg = tk.IntVar()
        self.year_beg = tk.Entry(year1frame, width=6)
        self.year_beg.insert(0, 2020)
        self.year_beg.pack(side=tk.LEFT)

        now = datetime.datetime.now()
        ttk.Label(year2frame, text='Year end', width=12).pack(side=tk.LEFT)
        self.year_end = tk.IntVar()
        self.year_end = tk.Entry(year2frame, width=6)
        self.year_end.insert(0, now.year)
        self.year_end.pack(side=tk.LEFT)

        ttk.Label(amountframe, text='Total').pack(side=tk.LEFT)
        self.amount_wid = tk.StringVar()
        amnt = ttk.Entry(amountframe, width=12, textvariable=self.amount_wid)
        amnt.insert(0, '')
        amnt.pack(side=tk.LEFT)

        self.txt = st.ScrolledText(txtframe, undo=True, width=40)
        self.txt['font'] = ('Arial', '10')
        self.txt.pack(expand=1, fill=tk.BOTH)

        formatHyperLink(self.txt, info_text)

# Initialise plot
        self.fig_time = Figure(figsize=(4., 3.), dpi=100)
        can_time = FigureCanvasTkAgg(self.fig_time, master=canframe)
        can_time._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        toolbar = nt2tk(can_time, canframe)
        toolbar.update()

        pbsmain.mainloop()


    def sel(self):
        self.bank = self.bank_wid.get().strip()
        self.dir_wid.delete(0, tk.END)
        try:
            from bank_path import dir_bank
            self.dir_wid.insert(0, dir_bank[self.bank])
        except:
            self.dir_wid.insert(0, os.getenv('HOME'))

    def info(self):
    
        self.txt.delete('1.0', tk.END)
        formatHyperLink(self.txt, info_text)

    def save_dir(self):
        try:
            from bank_path import dir_bank
        except:
            dir_bank = {}
        new_dir = self.dir_wid.get().strip()
        dir_bank[self.bank] = new_dir
        with open('bank_path.py', 'w') as f:
            f.write('dir_bank = { \\\n')
            for key, val in dir_bank.items():
                f.write("'%s': '%s', \\\n" %(key, val))
            f.write('}\n')
        
    def parse_year(self, dir_in):
        '''Check for given words in statements, case insensitive'''

        tot_year = 0
        out_str = ''
        logger.debug(dir_in)
        year = int(os.path.basename(dir_in))
        if self.bank == 'sskm' and year > 2021:
            self.bank = 'sskm2'

        for f_name in sorted(os.listdir(dir_in)):
            fname = '%s/%s' %(dir_in, f_name)
            pre, ext = os.path.splitext(fname)
            if (self.bank == 'sskm') and year == 2021:
                month = pre.split('_')[-1]
                if month in ('011', '012'):
                    self.bank = 'sskm2'
                    logger.debug('MONTH %s %s', month, self.bank)

            if ext.lower() != '.pdf':
                continue
            else:
                fpdf = fname
            fcsv = os.path.splitext(fpdf)[0] + '.csv'
            log = pdf2csv.pdf2csv(fpdf, fcsv, self.bank)
            if log is not None:
                self.txt.insert('insert', log)
            if self.bank in ('sskm', 'ksk'):
                tras = csv2tras_sskm(fcsv)
            elif self.bank == 'sskm2':
                tras = csv2tras_sskm2(fcsv)
            elif self.bank == 'diba':
                tras = csv2tras_diba(fcsv)
            elif self.bank == 'visa':
                tras = csv2tras_visa(fcsv)
            self.txt.insert('insert', fcsv+'\n') # git

# Parse transactions of a given statement
            for tra in tras:
                for key in ('descr', 'user', 'type'):
                    if key in tra.keys():
                        if self.word.upper() in tra[key].upper():
                            out_str = 'date: %s  ' %tra['date']
                            if tra['amount'] is not None:
                                tot_year += tra['amount']
                                out_str += '%9.2f\u20ac' %tra['amount']
                            out_str += '\n'
                            self.txt.insert('insert', out_str)
                            break
        self.txt.insert('insert', '\n%s\nkeyword "%s": %8.2f\u20ac\n\n' %(dir_in, self.word, tot_year))

        return tot_year


    def parse(self, plot=True):

        self.bank = self.bank_wid.get().strip()
        self.word = self.word_wid.get().strip()
        dir_root = self.dir_wid.get().strip()
        year_beg = int(self.year_beg.get())
        year_end = int(self.year_end.get())
        amount = []
        all_time= 0
        self.txt.delete('1.0', tk.END)
        for year in range(year_beg, year_end+1):
            dir_in = '%s/%d' %(dir_root, year)
            if os.path.isdir(dir_in):
                balance = self.parse_year(dir_in)
                self.txt.update()
                amount.append(balance)
                all_time += balance
            else:
                amount.append(0)
        self.amount_wid.set('%11.2f' %all_time)
        if plot:
            plot_time(year_beg, year_end, amount, self.fig_time)
            
if __name__ == '__main__':

    pbs_gui()

