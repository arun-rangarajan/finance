# coding: utf-8

from common import get_formatted, get_friendly_format

ticker = 'CB'

current_stock_price = 137
shares_out = 469.61 * 1e6
next_yr_FCF = 4.43 * 1e9 # estimate

# discount rate - use 8% for the best, 15% for the worst
r = 0.1

# FCF growth rates
rate_first_5_yrs = 0.04
rate_last_5_yrs = 0.03

# how confident are you in your analysis
margin_of_safety = 0.8

# perpetuity growth rate
g = 0.03

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
    discounted_fcfs.append(fcf / ((1 + r) ** (idx + 1)))
#print(get_formatted(discounted_fcfs))

perpetuity_value = fcfs[-1] * (1 + g) / (r - g)
discounted_perp_value = perpetuity_value / ((1 + r) ** 10)
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

