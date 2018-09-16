"""
Script calculates intrinsic value and MOS price for ticker using 
the discounted cash flow model.
Estimated values are set in the file specified below by 
the variable estimates_file_path.
The stock data TSV file from stockrow should be in ../data/.
"""

import csv
import os
import sys
import numpy as np
import common

ticker = 'FB'

data_file_path = "../data/{}.tsv".format(ticker)
estimates_file_path = '../estimates/dcf_estimates.csv'

for p in [data_file_path, estimates_file_path]:
    if not os.path.exists(p):
        print("File not found:", p)
        sys.exit(1)

row = None
with open(estimates_file_path, newline='') as csvfile:
    reader = csv.DictReader(filter(lambda row: row and row[0] != '#', csvfile))
    for r in reader:
        if r['ticker'] == ticker:
            row = r
            break
if not row:
    raise ValueError("Estimate for " + ticker + " not found in estimates file!")

current_stock_price = float(row['current_stock_price'])
discount_rate = float(row['discount_rate_pct']) / 100
rate_first_5_yrs = float(row['growth_rate1_pct']) / 100
rate_last_5_yrs = float(row['growth_rate2_pct']) / 100
perp_growth_rate = float(row['perpetuity_growth_rate_pct']) / 100
margin_of_safety = float(row['mos_factor_pct']) / 100

next_yr_FCF = None
if 'next_year_FCF' in row.keys() and row['next_year_FCF']:
    print("Speculative/growth company, so using FCF from file...")
    next_yr_FCF = common.sanitize_accounting_number(row['next_year_FCF'])

d = common.get_data_dict(data_file_path)

shares_out = 0
if d.get('Weighted Average Shs Out (Dil.)', None) and d['Weighted Average Shs Out (Dil.)'][-1]:
    shares_out = float(d['Weighted Average Shs Out (Dil.)'][-1])
else:
    shares_out = float(d['Weighted Average Shs Out'][-1])

if not next_yr_FCF:
    print('Steady company, so using past 10-yr FCF avg for next year...')
    next_yr_FCF = np.mean([x for x in d['FCF per Share'] if x]) * shares_out

print("---")
print("                     Ticker =", ticker)
print("              Discount rate =", discount_rate)
print("Growth rate for first 5 yrs =", rate_first_5_yrs)
print("Growth rate for last 5 yrs  =", rate_last_5_yrs)
print("     Perpetuity growth rate =", perp_growth_rate)
print("                 MOS factor =", margin_of_safety)
print("                Shares out. =", common.get_friendly_format(shares_out))
print("                Next yr FCF =", common.get_friendly_format(next_yr_FCF))
print("---")

fcfs = [next_yr_FCF]
for yr in range(2, 7):
    prev_fcf = fcfs[yr - 2]
    fcfs.append(prev_fcf * (1 + rate_first_5_yrs))
for yr in range(7, 11):
    prev_fcf = fcfs[yr - 2]
    fcfs.append(prev_fcf * (1 + rate_last_5_yrs))
#print(get_formatted(fcfs))

discounted_fcfs = []
for idx, fcf in enumerate(fcfs):
    discounted_fcfs.append(fcf / ((1 + discount_rate) ** (idx + 1)))
#print(get_formatted(discounted_fcfs))

perpetuity_value = fcfs[-1] * (1 + perp_growth_rate) / \
    (discount_rate - perp_growth_rate)
discounted_perp_value = perpetuity_value / ((1 + discount_rate) ** 10)
#print("Disc pv =", get_friendly_format(discounted_perp_value))

total_equity_value = sum(discounted_fcfs) + discounted_perp_value
intrinsic_value = round(total_equity_value / shares_out, 2)
print("Intrinsic value per share =", intrinsic_value)
mos_price = round(margin_of_safety * intrinsic_value, 2)
print("MOS price =", mos_price)
print("Current stock price =", current_stock_price)

if mos_price > current_stock_price:
    print("Good to buy")
else:
    print("Don't buy now")

