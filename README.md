This python GUI-based tool allows to browse bank statements, or any column-structured PDF files, if the format is rigid.

The app expects a directory structure of the type:
- <baseDir>/<bank_path>/2018
- <baseDir>/<bank_path>/2019
- <baseDir>/<bank_path>/2020
and the statements to be PDF files.

`banks.json` contains the actual sub-paths with the bank statements for each bank. Edit it according to your directory tree.<br>
`baseDir`, the common root directory for all banks, is set in `pbs.py`.

The package allows to parse several bank accounts. Each bank has its <bank_path>, this can be stored from the GUI and will be loaded on future usage.

PDF files are parsed with the `pdfplumber` package.

Supported banks: SSKM-Gyrokonto, Ing.Diba, SSKM-Visa-Kreditkarte, KSKMSE

Usage:
```
pip install parse_bank_statements
```

`$PBS_HOME/pbs.py`
or
`python`
```pycon
>>>from parse_bank_statements import pbs
>>>pbs.main()
```
