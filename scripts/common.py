import csv
import math
import re
import numpy as np

MILLION_RE = re.compile(r'[mM]$')
BILLION_RE = re.compile(r'[bB]$')

def get_friendly_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def get_formatted(vals):
    return [get_friendly_format(n) for n in vals]


def get_growth_rate(vals):
    vals = [v for v in vals if v]
    n = len(vals)
    a_1 = vals[0]
    a_n = vals[-1]
    if a_1 <= 0 or a_n <= 0:
        print("Can't compute FCF growth rate")
        return None
    rate = math.exp(math.log(a_n / a_1) / n) - 1
    return round(rate * 100, 1)


def sanitize(values, len_reqd):
    """
    Cleans up accounting numbers:
        - remove commas
        - replace % with actual numbers
        - negative numbers in parantheses
        - millions in m or M
        - billions in b or B
    """
    new_vals = []
    for v in values:
        new_val = None
        
        # remove all non-ASCII chars
        v = ''.join([i if ord(i) < 128 else '' for i in v])
        if not v:
            new_vals.append(None)
            continue
        v = v.replace(',', '')
        
        is_negative = False        
        if v.startswith('(') and v.endswith(')'):
            is_negative = True
            v = v.lstrip('(').rstrip(')')

        if v.endswith('%'):
            v = str(float(v.rstrip('%')) / 100)

        if MILLION_RE.search(v):
            v = v[0:-1]
            v = float(v) * 1e6
        else:
            if BILLION_RE.search(v):
                v = v[0:-1]
                v = float(v) * 1e9
        
        if is_negative:
            new_val = (-1) * float(v)
        else:
            new_val = float(v)

        new_val = round(new_val, 2)
        new_vals.append(new_val)
    
    assert(len(new_vals) == len_reqd)
    return new_vals


def get_data_dict(data_file_path):
    with open(data_file_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t', quotechar='"')
        header_line = next(reader)
        headers = [h for h in header_line if h]
        headers.reverse()
        n_cols = len(headers)
    
        d = {}
        d['headers'] = headers
        for row in reader:
            metric = row[0].strip()
            values = row[-n_cols:]
            values.reverse()
            if len(values) < n_cols:
                # print("Invalid:", metric)
                pass
            else:
                d[metric] = sanitize(values, n_cols)
    return d



def get_ratio(d, numerator, denominator, percent=False, round_digits=2):
    nums = d[numerator]
    dens = d[denominator]
    r = []
    for n, d in zip(nums, dens):
        if n is None or d is None:
            r.append(None)
        else:
            val = round(n / d, 2)
            if percent: val = val * 100
            if round_digits == 0: val = int(val)
            r.append(val)
    return r


def get_product(d, numerator, denominator):
    nums = d[numerator]
    dens = d[denominator]
    r = []
    for n, d in zip(nums, dens):
        r.append(n * d)
    return r


def get_fcf_to_sales_ratio(d):
    return get_ratio(d, 'FCF per Share', 'Sales per Share', percent=True, round_digits=0)


def get_debt_to_equity(d):
    return get_ratio(d, 'Total debt', 'Shareholders Equity')

