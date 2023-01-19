import os  # project tabula-py, requiring Java

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
            tabula.convert_into(fpdf, fcsv, output_format="csv", pages="all", area=bank.pdfArea, columns=bank.pdfColumns, silent=True)
            log = 'Converting %s into %s\n' %(fpdf, fcsv)

    return log
