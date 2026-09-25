This python GUI-based tool allows to browse bank statements, or any column-structured PDF files, if the format is rigid.

The app expects a directory structure of the type:
- <bank_statements_path>/2018
- <bank_statements_path>/2019
- <bank_statements_path>/2020
and the statements to be PDF.

The package allows to parse several bank accounts. Each bank has its <bank_statements_path>, this can be stored from the GUI and will be loaded on future usage.

PDF files are parsed with the package pdfplumber

Supported banks: SSKM-Gyrokonto, Ing.Diba, SSKM-Visa-Kreditkarte, KSKMSE

Usage:

pip install parse_bank_statements

Edit banks.py, inserting the actual full root-paths containing the bank statements

$PBS_HOME/pbs.py
