This python GUI-based tool allows to browse bank statements, or any column-structured PDF files, if the format is rigid.

The app expects a directory structure of the type:
    <bank_statements_path>/2018
    <bank_statements_path>/2019
    <bank_statements_path>/2020
and the statements to be PDF.
Each bank has its <bank_statements_path>, this can be stored from the GUI and will be loaded on future usage.

PDF files are converted (una tantum) into CSV, based on the open source java-based package tabula-py (see https://pypi.org/project/tabula-py).

Supported banks: SSKM-Gyrokonto, Ing.Diba, SSKM-Visa-Kreditkarte
