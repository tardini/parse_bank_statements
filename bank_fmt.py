help = """
AREA boundaries: (top-y, left-x, bottom-y, right-x).
COLUMNS separators (x-positions).
To find them out for the specific PDF column format of a given bank's statements, use e.g. gimp, mode typogr.points.
Define the PAGE END string in 'end_str'
"""
 
iban_sskm = 'Gläubiger-ID:'

mand_diba = 'Mandat:'
ref_diba  = 'Referenz:'

area = { \
    'sskm': (139.5, 60, 707.5, 573), \
    'diba': (190, 67, 765, 568), \
    'visa': (300, 37, 750, 590) }

cols = { \
    'sskm': (116.4, 163.3, 360, 465.4), \
    'diba': (131, 507), \
    'visa': (80, 120, 280, 360, 450, 530) }

end_str = {'sskm': 'Der Kon', 'diba': 'Kunden-In', 'visa': 'Sehr'}

