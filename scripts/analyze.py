import os
import sys
import csv
import re
import pandas as pd
from collections import OrderedDict
import math
from common import get_formatted

ticker = 'KSU'

infile = "../data/{}.tsv".format(ticker)
if not os.path.exists(infile):
    print("File not found:", infile)
    sys.exit(1)

MILLION_RE = re.compile(r'[mM]$')
BILLION_RE = re.compile(r'[bB]$')


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


def get_fcf_to_sales_ratio(d):
    return get_ratio(d, 'FCF per Share', 'Sales per Share', percent=True, round_digits=0)


def get_debt_to_equity(d):
    return get_ratio(d, 'Total debt', 'Shareholders Equity')


def get_growth_rate(vals):
    vals = [v for v in vals if v]
    n = len(vals)
    a_1 = vals[0]
    a_n = vals[-1]
    if a_1 <= 0 or a_n <= 0:
        print("Can't compute FCF growth rate")
        return None
    return math.exp(math.log(a_n / a_1) / n) - 1

with open(infile, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t', quotechar='"')
    header_line = next(reader)
    headers = [h for h in header_line if h]
    headers.reverse()
    n_cols = len(headers)

    d = {}
    for row in reader:
        metric = row[0].strip()
        values = row[-n_cols:]
        values.reverse()
        if len(values) < n_cols:
            # print("Invalid:", metric)
            pass
        else:
            d[metric] = sanitize(values, n_cols)
    
    fcf_to_sales = get_fcf_to_sales_ratio(d)
    fcf_to_sales = ['{}%'.format(f) for f in fcf_to_sales]
    debt_to_equity = get_debt_to_equity(d)
    
    df = pd.DataFrame(OrderedDict([
        ('Dt', headers),
        ('FCF/Sales', fcf_to_sales),
        ('FCF/share', d['FCF per Share']),
        ('CapEx', get_formatted(d['Capital Expenditure'])),
        ('EPS', d['EPS']),
        ('ROE', d['ROE']),
        ('ROA', d['ROA']),
        ('ROIC', d['ROIC']),
        ('D/E', debt_to_equity)]))
    print(df)        

    print('---')
    print('FCF growth rate =', get_growth_rate(d['FCF per Share']))
