#!/usr/bin/env python

import os, sys, csv # project tabula-py, requiring Java
import tkinter as tk
import tkinter.scrolledtext as st
from tkinter import ttk
from tkinter import filedialog as tkfd
import bank_fmt as bd
import numpy as np
import matplotlib.pylab as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
try:
    from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as nt2tk
except:
    from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg as nt2tk


info_text = \
'''The app expects a directory structure of the type:
    <bank_statements_path>/2018
    <bank_statements_path>/2019
    <bank_statements_path>/2020
and the statements to be PDF.
Each bank has its <bank_statements_path>, this can be stored from the GUI and will be loaded in future usage.

PDF files are converted (una tantum) into CSV, based on the open source java-based package tabula-py (see https://pypi.org/project/tabula-py).

Supported banks: SSKM-Gyrokonto, Ing.Diba, SSKM-Visa-Kreditkarte
'''


def pdf2csv(fpdf, fcsv, bank):
    '''Convert a PDF statement into csv text format'''
    import tabula

    if not os.path.isfile(fpdf):
        log = 'File %s not found\n' %fpdf
    else:
        if os.path.isfile(fcsv):
            log = ''
        else:
            tabula.convert_into(fpdf, fcsv, output_format="csv", pages="all", area=bd.area[bank], columns=bd.cols[bank], silent=True)
            log = 'Converting %s into %s\n' %(fpdf, fcsv)

    return log


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


def isdate_y4(str_in):
    '''Check whether an input string has a date format'''

    str_in = str_in.strip()
    is_date = False
    if len(str_in) == 10:
        if str_in[2] == '.' and str_in[5] == '.':
            try:
                day   = int(str_in[0:2])
                month = int(str_in[3:5])
                year  = int(str_in[6:10])
                is_date = True
            except:
                is_date = False
    return is_date


def isdate_y2(str_in):
    '''Check whether an input string has a date format'''

    str_in = str_in.strip()
    is_date = False
    if len(str_in) == 8:
        if str_in[2] == '.' and str_in[5] == '.':
            try:
                day   = int(str_in[0:2])
                month = int(str_in[3:5])
                year  = int(str_in[6:8])
                is_date = True
            except:
                is_date = False
    return is_date


def amount_sskm(str_in):
    '''Convert string to float (money amount) for bank SSKM'''

    str_in = str_in.strip().replace('.', '').replace(',', '.')
    if str_in == '':
        return None
    try:
        money = float(str_in[:-1])
    except:
        print('Error converting %s to float' %str_in)
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
        print('Error converting %s to float' %str_in)
        money = None
    return money


def csv2tras_sskm(fcsv):
    '''Split a statement into a list of transaction dictionaries (bank SSKM)'''

    transactions = []
    with open(fcsv, newline='') as csvfile:
        csvreader = csv.reader(csvfile, quotechar='"')
        for line in csvreader:
            if len(line) < 5:
                print('LINE too short', line)
                continue
            date       = line[0].strip()
            date_val   = line[1].strip()
            descr_line = line[2].strip()
            amount_out = line[3].strip()
            amount_in  = line[4].strip()
            if date == '':
                if 'tra' in locals():
                    if 'descr' in tra.keys():
                        if descr_line != '':
                            tra['descr'] += '\n' + descr_line
            elif isdate_y4(date_val): # new transaction
                if 'tra' in locals():
                    if bd.iban_sskm in tra['descr']:
                        descr, tra['iban'] = tra['descr'].split(bd.iban_sskm, 1)
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
                    transactions.append(tra)
                tra = {}
                if not isdate_y4(date):
                    try:
                        date = date.split()[1]
                    except:
                        pass
                tra['date'] = date
                tra['date_currency'] = date_val
                tra['descr'] = descr_line
                minus = amount_sskm(amount_in)
                if minus is not None:
                    tra['amount'] = minus
                else:
                    tra['amount'] = amount_sskm(amount_out)
            elif bd.end_str['sskm'] in date:
                if 'tra' in locals():
                    transactions.append(tra)
                break
                
    return transactions


def csv2tras_visa(fcsv):
    '''Split a statement into a list of transaction dictionaries (bank SSKM)'''

    transactions = []
    with open(fcsv, newline='') as csvfile:
        csvreader = csv.reader(csvfile, quotechar='"')
        for line in csvreader:
            date       = line[0].strip()
            date_val   = line[1].strip()
            descr_line = line[2].strip()
            currency   = line[3].strip()
            amount_raw = line[4].strip()
            exchange   = line[5].strip()
            amount_eur = line[6].strip()
            if date == '':
                if 'tra' in locals():
                    if 'descr' in tra.keys():
                        if descr_line != '':
                            tra['descr'] += '\n' + descr_line
            elif isdate_y2(date_val): # new transaction

                tra = {}
                if not isdate_y2(date):
                    try:
                        date = date.split()[1]
                    except:
                        pass
                tra['date'] = date
                tra['date_currency'] = date_val
                tra['descr']         = descr_line
                tra['currency']      = currency
                tra['amount_raw']    = amount_raw
                tra['exchange']      = exchange
                tra['amount']        = amount_sskm(amount_eur) 
            elif bd.end_str['visa'] in date:
                if 'tra' in locals():
                    transactions.append(tra)
                break
                
    return transactions


def csv2tras_diba(fcsv):
    '''Split a statement into a list of transaction dictionaries (bank Ing.DIBA)'''

    transactions = []
    line_old = ''
    new_trans = 1
    with open(fcsv, newline='') as csvfile:
        csvreader = csv.reader(csvfile, quotechar='"')
        for line in csvreader:

            date = line[0].strip()

            if isdate_y4(date) and new_trans: # new transaction
                if 'tra' in locals():
                    transactions.append(tra)
                tra = {}
                tra['date'] = date
                tra['type'], tra['user'] = line[1].split(' ', 1)
                tra['descr'] = ''
                tra['amount'] = amount_diba(line[2])
            elif bd.end_str['diba'] in date:
                if 'tra' in locals():
                    transactions.append(tra)
                break
            else:
                if isdate_y4(date): # second line
                    tra['date_currency'] = date
                descr_line = line[1].strip()
                if 'tra' in locals():
                    if 'descr' in tra.keys():
                        if descr_line != '':
                            if bd.mand_diba in descr_line:
                                tra['mandat'] = descr_line.split(bd.mand_diba, 1)[1].strip()
                            elif bd.ref_diba in descr_line:
                                tra['reference'] = descr_line.split(bd.ref_diba, 1)[1].strip()
                            else:
                                tra['descr'] += '\n' + descr_line
            if isdate_y4(date):
                new_trans = isdate_y4(date) - new_trans 
            line_old = line

    return transactions


def about():

    import tkhyper
    mytext = 'Documentation at the <a href="https://www2.ipp.mpg.de/~git/pcsv/index.html">Statement Parser</a>'
    h = tkhyper.HyperlinkMessageBox("Help", mytext, "340x60")


class pcsv_gui:


    def __init__(self):


        pcsvmain = tk.Tk()
        import pcsv_style
        pcsvmain.title('Bank-statement parser')
        pcsvmain.geometry('800x600')
        pcsvmain.configure(background=pcsv_style.frc)

# Menubar

        menubar  = tk.Menu(pcsvmain)
        filemenu = tk.Menu(menubar, tearoff=0)

        filemenu.add_command(label="Parse statements", command=self.parse)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=sys.exit)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Info"    , command=self.info)
        helpmenu.add_command(label="Web docu", command=about)

        menubar.add_cascade(label = "File", menu=filemenu)
        menubar.add_cascade(label = "Help", menu=helpmenu)

        menubar.configure(bg=pcsv_style.tbc)
        pcsvmain.config(menu = menubar)

        btframe     = ttk.Frame(pcsvmain)
        bankframe   = ttk.Frame(pcsvmain)
        wordframe   = ttk.Frame(pcsvmain)
        dirframe    = ttk.Frame(pcsvmain)
        year1frame  = ttk.Frame(pcsvmain)
        year2frame  = ttk.Frame(pcsvmain)
        amountframe = ttk.Frame(pcsvmain)
        outframe    = ttk.Frame(pcsvmain)
        
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
        for rb in bank1, bank2, bank3:
            rb.pack(side=tk.LEFT)

        ttk.Label(wordframe, text='Keyword').pack(side=tk.LEFT)
        self.word_wid = tk.Entry(wordframe, width=40)
        self.word_wid.insert(0, 'plasma')
        self.word_wid.pack(side=tk.LEFT)

        ttk.Label(dirframe, text='Start dir', width=12).pack(side=tk.LEFT)
        self.dir_wid = tk.Entry(dirframe, width=40)
        self.sel()
        self.dir_wid.pack(side=tk.LEFT)
        ttk.Button(dirframe, text='Save', command=self.save_dir).pack(side=tk.LEFT)

        ttk.Label(year1frame, text='Year start', width=12).pack(side=tk.LEFT)
        self.year_beg = tk.IntVar()
        self.year_beg = tk.Entry(year1frame, width=6)
        self.year_beg.insert(0, 2016)
        self.year_beg.pack(side=tk.LEFT)

        ttk.Label(year2frame, text='Year end', width=12).pack(side=tk.LEFT)
        self.year_end = tk.IntVar()
        self.year_end = tk.Entry(year2frame, width=6)
        self.year_end.insert(0, 2020)
        self.year_end.pack(side=tk.LEFT)

        ttk.Label(amountframe, text='Total').pack(side=tk.LEFT)
        self.amount_wid = tk.StringVar()
        amnt = ttk.Entry(amountframe, width=12, textvariable=self.amount_wid)
        amnt.insert(0, '')
        amnt.pack(side=tk.LEFT)

        self.txt = st.ScrolledText(txtframe, undo=True, width=40)
        self.txt['font'] = ('Arial', '10')
        self.txt.pack(expand=1, fill=tk.BOTH)

# Initialise plot
        self.fig_time = Figure(figsize=(4., 3.), dpi=100)
        can_time = FigureCanvasTkAgg(self.fig_time, master=canframe)
        can_time._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        toolbar = nt2tk(can_time, canframe)
        toolbar.update()

        pcsvmain.mainloop()


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
        self.txt.insert(tk.INSERT, info_text)

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
        for f_name in sorted(os.listdir(dir_in)):
            fname = '%s/%s' %(dir_in, f_name)
            ext = os.path.splitext(fname)[1]
            
            if ext.lower() != '.pdf':
                continue
            else:
                fpdf = fname
            fcsv = os.path.splitext(fpdf)[0] + '.csv'
            log = pdf2csv(fpdf, fcsv, self.bank)
            self.txt.insert(tk.INSERT, log)
            if self.bank == 'sskm':
                tras = csv2tras_sskm(fcsv)
            elif self.bank == 'diba':
                tras = csv2tras_diba(fcsv)
            elif self.bank == 'visa':
                tras = csv2tras_visa(fcsv)

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
                            self.txt.insert(tk.INSERT, out_str)
                            break
        self.txt.insert(tk.INSERT, '\n%s\nkeyword "%s": %10.4f\u20ac\n\n' %(dir_in, self.word, tot_year))

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

    pcsv_gui()

