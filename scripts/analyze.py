import os
import sys
import pandas as pd
from tabulate import tabulate
import numpy as np
from collections import OrderedDict
import common

ticker = 'CB'

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
    ('Dt', d['headers']),
    ('FCF/Sales', fcf_to_sales),
    ('FCF/share', d['FCF per Share']),
    ('CapEx', common.get_formatted(d['Capital Expenditure'])),
    ('EPS', d['EPS']),
    ('ROE', d['ROE']),
    ('ROA', d['ROA']),
    #('ROIC', d['ROIC']),
    ('D/E', debt_to_equity),
    ('Net Income', common.get_formatted(d['Net Income']))
]))
print(ticker)
print(tabulate(df, headers='keys', tablefmt='psql'))   

fcfs = common.get_product(d, 'FCF per Share', 'Weighted Average Shs Out')
print('Avg FCF =', common.get_friendly_format(np.mean(fcfs)))
print('FCF growth rate = {}%'.format(common.get_growth_rate(d['FCF per Share'])))
print('Net income growth rate = {}%'.format(common.get_growth_rate(d['Net Income'])))
