This python GUI-based tool allows to browse bank statements, or any column-structured PDF files, if the format is rigid.

The app expects a directory structure of the type:
- <bank_statements_path>/2018
- <bank_statements_path>/2019
- <bank_statements_path>/2020
and the statements to be PDF.

The package allows to parse several bank accounts. Each bank has its <bank_statements_path>, this can be stored from the GUI and will be loaded on future usage.

Docu at https://www2.ipp.mpg.de/~git/pbs/index.html

PDF files are converted (una tantum) into CSV, based on the open source java-based package tabula-py (see https://pypi.org/project/tabula-py). If you do not need this conversion because you have csv's, you do not need tabula_py.

Supported banks: SSKM-Gyrokonto, Ing.Diba, SSKM-Visa-Kreditkarte, KSKMSE

Usage:

pip install parse_bank_statements

Edit bank_path.py, inserting the actual full paths containing the bank statements (excluding the years' subdirs) <bank_statements_path1>, <bank_statements_path2>, ...

python
>>>from parse_bank_statements import parse_statements as pbs
>>>pbs.pbs_gui()
