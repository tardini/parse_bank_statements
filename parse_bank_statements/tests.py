import logging, json
from pathlib import Path
import statement

fmt = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s: %(message)s', '%H:%M:%S')
logger = logging.getLogger('PBS')
logger.setLevel(level=logging.INFO)
if not logger.handlers:
    hnd = logging.StreamHandler()
    hnd.setFormatter(fmt)
    logger.addHandler(hnd)

# Need only one instanciation, all is static therein

pbs_home = Path(__file__).resolve().parent
fjson = pbs_home / 'banks.json'
with open(fjson, 'r') as f:
    banks_d = json.load(f)

sskm = banks_d['SSKM']
ksm  = banks_d['KSKMSE']
diba = banks_d['DIBA']
visa = banks_d['VISA']

run_easy_tests = 1

if run_easy_tests:
    fpdf1 = '/shares/users/private/git/bank/sskm/gk/2026/Konto_0000131409-Auszug_2026_0001.PDF'
    fpdf2 = '/shares/users/private/git/bank/sskm/gk/2016/Konto_131409-Auszug_2016_001.PDF'
    for fpdf in (fpdf1, fpdf2):
        df = statement.fromFile(sskm, fpdf)
        print(df.columns)
        print(df['amount'])
        print(df['descr'])

    fpdf1 = '/shares/users/private/git/bank/kskmse/2018/Konto_28079358-Auszug_2018_007.PDF'
    for fpdf in (fpdf1,):
        df = statement.fromFile(ksm, fpdf)
        print(df.columns)
        print(df['amount'])
        print(df['descr'])

    fpdf1 = '/shares/users/private/git/bank/diba/2025/10_Oktober25.pdf'
    fpdf2 = '/shares/users/private/git/bank/diba/2018/12_Dez18.pdf' # superscripts, solved by exact cropping of the right edge
    for fpdf in (fpdf1, fpdf2):
        df = statement.fromFile(diba, fpdf)
        print(df.columns)
        print(df['amount'])
        print(df['descr'])

    fpdf1 = '/shares/users/private/git/bank/sskm/kk/2015/Abrechnung_4908_1215_20150105.PDF'
    fpdf2 = '/shares/users/private/git/bank/sskm/kk/2015/Abrechnung_4908_1215_20150902.PDF'
    fpdf3 = '/shares/users/private/git/bank/sskm/kk/2015/Abrechnung_4908_1215_20151202.PDF' # "None" Issue (Jahresbeitrag): solved
    for fpdf in (fpdf1, fpdf2, fpdf3):
        df = statement.fromFile(visa, fpdf)
        print(df.columns)
        print(df['amount'])
        print(df['descr'])

# Issues

issues = [1, 1]

if issues[0]:
    fpdf = '/shares/users/private/git/bank/diba/2025/08_August25.pdf' # alignment issue at page 9
    df = statement.fromFile(diba, fpdf)
    print(df.columns)
    print(df['amount'])
    
if issues[1]:
    fpdf = '/shares/users/private/git/bank/sskm/kk/2016/Abrechnung_4908_1215_20160503.PDF' # O statements
    df = statement.fromFile(visa, fpdf)
    print(df.columns)
    print(df['amount'])
   
