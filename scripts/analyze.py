"""
Script outputs fundamental metrics for companies.
Set variable ticker below and populate the TSV data 
from stockrow for the ticker in the folder ../data/
"""

import os
import sys
import pandas as pd
from tabulate import tabulate
import numpy as np
from collections import OrderedDict
import common

ticker = 'MSFT'

data_file = "../data/{}.tsv".format(ticker)
if not os.path.exists(data_file):
    print("File not found:", data_file)
    sys.exit(1)


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

d = common.get_data_dict(data_file)
    
fcf_to_sales = common.get_fcf_to_sales_ratio(d)
fcf_to_sales = ['{}%'.format(f) for f in fcf_to_sales]
debt_to_equity = common.get_debt_to_equity(d)

df = pd.DataFrame(OrderedDict([
    ('Date', d['headers']),
    ('ROA', common.get_as_pct(d['ROA'])),
    ('ROE', common.get_as_pct(d['ROE'])),
    ('ROIC', common.get_as_pct(d.get('ROIC', None))),
    ('ROIC (computed)', common.get_roic(d)),
    ('FCF/Sales', fcf_to_sales),
    ('FCF/share', d['FCF per Share']),
    ('CapEx', common.get_formatted(d['Capital Expenditure'])),
    ('EPS', d['EPS']),    
    ('D/E', debt_to_equity),
    ('Revenue', common.get_formatted(d['Revenue'])),
    ('Net Income', common.get_formatted(d['Net Income'])),
]))
print(ticker)
print(tabulate(df, headers='keys', tablefmt='psql'))   

fcfs = common.get_product(d, 'FCF per Share', 'Weighted Average Shs Out')
print('               Avg FCF =', common.get_friendly_format(np.nanmean(fcfs)))
print('       FCF growth rate = {}%'.format(common.get_growth_rate(d['FCF per Share'])))
print('Net income growth rate = {}%'.format(common.get_growth_rate(d['Net Income'])))
print('   Revenue growth rate = {}%'.format(common.get_growth_rate(d['Revenue'])))

if 'Total liabilities' in d.keys():
    print('---')
    print("Graham's net-net")
    price_to_ncavs = []
    for cash, liab, mkt_cap in zip(d['Cash and short-term investments'], 
                                   d['Total liabilities'], 
                                   d['Market Cap']):
        if cash and cash > 0 and liab and liab > 0:
            price_to_ncavs.append(round(mkt_cap / (cash - liab), 2))
    price_to_ncavs.reverse()
    print("Price-to-NCAV =", price_to_ncavs)
    print('---')

