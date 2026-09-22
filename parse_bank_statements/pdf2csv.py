import os, json  # project tabula-py, requiring Java

src_dir = os.path.dirname(os.path.abspath(__file__))
json_file = f'{src_dir}/banks.json'
with open(json_file) as json_data:
    banks_d = json.load(json_data)


def pdf2csv(fpdf, fcsv, bank_label):
    '''Convert a PDF statement into csv text format'''

    bank_geom = banks_d[bank_label]
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
            tabula.convert_into(fpdf, fcsv, output_format="csv", pages="all", area=bank_geom['pdfArea'], columns=bank_geom['pdfColumns'], silent=True)
            log = 'Converting %s into %s\n' %(fpdf, fcsv)

    return log
