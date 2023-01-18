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


def isdate(str_in):

    return (isdate_y4(str_in) or isdate_y2(str_in))
