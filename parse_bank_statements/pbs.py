#!/usr/bin/env python

import os, sys, re, webbrowser, datetime, logging
from pathlib import Path
import encodings.utf_8

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup,
    QPlainTextEdit, QAction
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCharFormat

from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.figure import Figure
from parse_bank_statements import banks
from parse_bank_statements import __version__ as version

pbs_home = Path(__file__).resolve().parent

info_text = \
'''PARSE BANK STATEMENTS

The app expects a directory structure of the type:
    <bank_statements_path>/2018
    <bank_statements_path>/2019
    <bank_statements_path>/2020
and the statements to be PDF.
Each bank has its <bank_statements_path>, this can be stored from the GUI and will be loaded on future usage.

Supported banks: SSKM-Gyrokonto, Ing.Diba, SSKM-Visa-Kreditkarte, KSKMSE

Repository <a href="https://github.com/tardini/parse_bank_statements.git">PBS github</a>
'''

os.environ['BROWSER'] = '/usr/bin/google-chrome'

baseDir = Path('/shares/users/private/git/bank')
if not baseDir.is_dir():
    baseDir = Path.home() / 'bank'

fmt = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s: %(message)s', '%H:%M:%S')
logger = logging.getLogger('PBS')
logger.setLevel(level=logging.INFO)
if not logger.handlers:
    hnd = logging.StreamHandler()
    hnd.setFormatter(fmt)
    logger.addHandler(hnd)


def plot_time(year_beg, year_end, amount, fig_time):

    fig_time.clf()
    fig_time.subplots_adjust(
        left=0.15, bottom=0.15, right=0.95, top=0.92, hspace=0
    )

    ax = fig_time.add_subplot(1, 1, 1)
    ax.set_xlabel('Year')
    ax.set_ylabel('Money €')

    xax = ax.get_xaxis()
    xax.grid(True, which='major')
    xax.set_major_locator(MaxNLocator(integer=True))

    if (max(amount) > 0) and (min(amount) >= 0):
        ax.set_ylim([0, 1.1 * max(amount)])
    elif (min(amount) < 0) and (max(amount) <= 0):
        ax.set_ylim([1.1 * min(amount), 0])

    ax.plot(range(year_beg, year_end + 1), amount, color='g', marker='o')

    ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    ax.yaxis.major.formatter._useMathText = True

    fig_time.canvas.draw()


class PBSGui(QMainWindow):

    def __init__(self):

        super().__init__()

        logger.info('Using version %s', version)
        logger.info('PBS home %s', pbs_home)

        self.setWindowTitle('Bank-statement-parser')
        self.resize(1000, 800)

        self._create_menu()
        self._create_widgets()

        self.sel()

    # ------------------------------------------------------------------
    # GUI creation
    # ------------------------------------------------------------------

    def _create_menu(self):

        menubar = self.menuBar()

        filemenu = menubar.addMenu('File')
        parse_action = QAction('Parse statements', self)
        parse_action.triggered.connect(self.parse)
        filemenu.addAction(parse_action)
        filemenu.addSeparator()
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        filemenu.addAction(exit_action)

        helpmenu = menubar.addMenu('Help')
        info_action = QAction('Info', self)
        info_action.triggered.connect(self.info)
        helpmenu.addAction(info_action)

    def _create_widgets(self):

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        # --------------------------------------------------------------
        # Parse button
        # --------------------------------------------------------------

        bt_layout = QHBoxLayout()

        parse_button = QPushButton('Parse statements')
        parse_button.setFixedWidth(130)
        parse_button.clicked.connect(self.parse)

        bt_layout.addWidget(parse_button)
        bt_layout.addStretch()

        main_layout.addLayout(bt_layout)

        # --------------------------------------------------------------
        # Start directory
        # --------------------------------------------------------------

        dir_layout = QHBoxLayout()

        label = QLabel('Start dir')
        label.setFixedWidth(80)
        dir_layout.addWidget(label)

        self.dir_wid = QLineEdit()
        self.dir_wid.setMinimumWidth(400)

        dir_layout.addWidget(self.dir_wid)
        dir_layout.addStretch()

        main_layout.addLayout(dir_layout)

        # --------------------------------------------------------------
        # Bank
        # --------------------------------------------------------------

        bank_layout = QHBoxLayout()

        bank_layout.addWidget(QLabel('Bank'))

        self.bank_group = QButtonGroup(self)

        for text, value in [
            ('SSKM', 'sskm'),
            ('DiBa', 'diba'),
            ('Visa', 'visa'),
            ('KSKMSE', 'kskmse'),
        ]:
            rb = QRadioButton(text)
            rb.value = value
            self.bank_group.addButton(rb)
            bank_layout.addWidget(rb)
            rb.toggled.connect(self.sel)

            if value == 'sskm':
                rb.setChecked(True)

        bank_layout.addStretch()
        main_layout.addLayout(bank_layout)

        # --------------------------------------------------------------
        # Keyword
        # --------------------------------------------------------------

        word_layout = QHBoxLayout()

        word_layout.addWidget(QLabel('Keyword'))

        self.word_wid = QLineEdit('plasma')
        self.word_wid.setMinimumWidth(400)

        word_layout.addWidget(self.word_wid)
        word_layout.addStretch()

        main_layout.addLayout(word_layout)

        # --------------------------------------------------------------
        # Year start
        # --------------------------------------------------------------

        year1_layout = QHBoxLayout()

        label = QLabel('Year start')
        label.setFixedWidth(80)
        year1_layout.addWidget(label)

        self.year_beg = QLineEdit('2015')
        self.year_beg.setFixedWidth(60)

        year1_layout.addWidget(self.year_beg)
        year1_layout.addStretch()

        main_layout.addLayout(year1_layout)

        # --------------------------------------------------------------
        # Year end
        # --------------------------------------------------------------

        year2_layout = QHBoxLayout()

        label = QLabel('Year end')
        label.setFixedWidth(80)
        year2_layout.addWidget(label)

        self.year_end = QLineEdit(str(datetime.datetime.now().year))
        self.year_end.setFixedWidth(60)

        year2_layout.addWidget(self.year_end)
        year2_layout.addStretch()

        main_layout.addLayout(year2_layout)

        # --------------------------------------------------------------
        # Total
        # --------------------------------------------------------------

        amount_layout = QHBoxLayout()

        amount_layout.addWidget(QLabel('Total'))

        self.amount_wid = QLineEdit()
        self.amount_wid.setFixedWidth(120)
        self.amount_wid.setReadOnly(True)

        amount_layout.addWidget(self.amount_wid)
        amount_layout.addStretch()

        main_layout.addLayout(amount_layout)

        # --------------------------------------------------------------
        # Output + plot
        # --------------------------------------------------------------

        output_layout = QHBoxLayout()

        self.txt = QPlainTextEdit()
        self.txt.setUndoRedoEnabled(True)
        self.txt.setFont(QFont('Arial', 10))
        self.txt.setReadOnly(True)
        self.txt.setStyleSheet("color: black;")
        self.txt.setFixedWidth(300)

        output_layout.addWidget(self.txt, 1)

        # Matplotlib
        self.fig_time = Figure(figsize=(4., 3.), dpi=100)

        self.can_time = FigureCanvasQTAgg(self.fig_time)
        self.toolbar = NavigationToolbar2QT(self.can_time, self)

        plot_layout = QVBoxLayout()
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.can_time)

        plot_widget = QWidget()
        plot_widget.setLayout(plot_layout)

        output_layout.addWidget(plot_widget, 1)

        main_layout.addLayout(output_layout, 1)

        self._set_info_text()

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    def _set_info_text(self):

        self.txt.clear()

        # QPlainTextEdit doesn't interpret HTML, so handle the
        # informational text separately.
        cursor = self.txt.textCursor()

        start = 0

        pattern = re.compile(
            r'<a href="(?P<address>.*?)">(?P<title>.*?)</a>'
        )

        for match in pattern.finditer(info_text):

            cursor.insertText(info_text[start:match.start()])
            url = match.group('address')
            title = match.group('title')

            # QPlainTextEdit doesn't support clickable rich-text
            # hyperlinks, so make the repository link clickable
            # through the QTextCursor's anchor formatting.
            from PyQt5.QtGui import QTextCharFormat, QColor

            qfmt = QTextCharFormat()
            qfmt.setForeground(QColor('blue'))
            qfmt.setFontUnderline(True)
            qfmt.setAnchor(True)
            qfmt.setAnchorHref(url)

            cursor.insertText(title, qfmt)
            start = match.end()

        cursor.insertText(info_text[start:])
        self.txt.setTextCursor(cursor)
        plain = QTextCharFormat()
        cursor.insertText(' ', plain)
        self.txt.setTextCursor(cursor)


    def _selected_bank(self):
        button = self.bank_group.checkedButton()
        return button.value

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def sel(self):
        button = self.bank_group.checkedButton()
        if button is None:
            return
        self.bank_label = button.value
        self.bank = getattr(banks, self.bank_label.upper())
        rootDir = baseDir / self.bank.rootDir
        self.dir_wid.setText(str(rootDir))

    def info(self):
        self._set_info_text()

    def parse_year(self, dir_in):
        '''Check for given words in statements, case insensitive'''

        logger.debug(dir_in)

        year = int(Path(dir_in).name)

        tot_year = 0
        for fname in sorted(f for f in dir_in.iterdir() if f.is_file()):
            pre = fname.with_suffix('')
            ext = fname.suffix
            if ext.lower() != '.pdf':
                continue
            fpdf = fname
            tras = self.bank()
            df = banks.fromPDF(tras, fpdf)
            df_filtered = df[
                df["descr"].str.contains(
                    self.word,
                    case=False,
                    na=False,
                    regex=False
                )
            ]

            out_str = ( df_filtered[["date", "amount"]].to_string(index=False, header=False) )
            self.txt.appendPlainText(out_str)
            tot_year += df_filtered["amount"].sum()

        self.txt.appendPlainText(
            '\n%s\nkeyword "%s": %8.2f€\n'
            % (dir_in, self.word, tot_year)
        )

        return tot_year

    def parse(self):

        self.word = self.word_wid.text().strip()

        dir_root = Path(self.dir_wid.text())
        year_beg = int(self.year_beg.text())
        year_end = int(self.year_end.text())

        amount = []
        all_time = 0

        self.txt.clear()

        for year in range(year_beg, year_end + 1):
            dir_in = dir_root / f'{year}'
            if dir_in.is_dir():
                balance = self.parse_year(dir_in)
                QApplication.processEvents()
                amount.append(balance)
                all_time += balance
            else:
                amount.append(0)

        self.amount_wid.setText('%11.2f' % all_time)

        plot_time(year_beg, year_end, amount, self.fig_time)


def main():

    app = QApplication(sys.argv)
    window = PBSGui()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
