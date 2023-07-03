import pandas as pd

MAX_INT = 1000000000000000

property_tax_values = pd.DataFrame({
    'Hawaii': [0.28],
    'Alabama': [0.41],
    'Colorado':	[0.51],
    'Louisiana': [0.55],
    'District of Columbia':	[0.56],
    'South Carolina': [0.57],
    'Delaware':	[0.57],
    'West Virginia': [0.58],
    'Nevada':	[0.60],
	'Wyoming':	[0.61],
	'Arkansas':	[0.62],
	'Utah':	[0.63],
	'Arizona':	[0.66],
	'Idaho':	[0.69],
	'Tennessee':	[0.71],
	'California':	[0.76],
	'New Mexico':	[0.80],
	'Mississippi':	[0.81],
	'Virginia':	[0.82],
	'Montana':	[0.84],
	'North Carolina': [0.84],
	'Indiana':	[0.85],
	'Kentucky':	[0.86],
	'Florida':	[0.89],
	'Oklahoma':	[0.90],
	'Georgia':	[0.92],
	'Missouri':	[0.97],
	'Oregon':	[0.97],
	'North Dakota':	[0.98],
	'Washington':	[0.98],
	'Maryland':	[1.09],
	'Minnesota':	[1.12],
	'Alaska':	[1.19],
	'Massachusetts':	[1.23],
	'South Dakota':	[1.31],
	'Maine':	[1.36],
	'Kansas':	[1.41],
	'Michigan':	[1.54],
	'Ohio':	[1.56],
	'Iowa':	[1.57],
	'Pennsylvania':	[1.58],
	'Rhode Island':	[1.63],
	'New York':	[1.72],
	'Nebraska':	[1.73],
	'Texas':	[1.80],
	'Wisconsin':	[1.85],
	'Vermont':	[1.90],
	'Connecticut':	[2.14],
	'New Hampshire':	[2.18],
	'Illinois':	[2.27],
	'New Jersey':	[2.49],
})


def calculate_income_tax_amount(income, state, filing_status, itemized_deduction_amount = None):
    federal_income_tax_brackets = pd.read_csv("tax_brackets/national_income_tax_brackets.csv")
    federal_income_tax_brackets = federal_income_tax_brackets[federal_income_tax_brackets["filing_status"] == filing_status]
    if filing_status == "Married":
        state_income_tax_brackets = pd.read_csv("tax_brackets/single_state_income_tax_brackets.csv").dropna()
    else:
        state_income_tax_brackets = pd.read_csv("tax_brackets/married_state_income_tax_brackets.csv").dropna()
    # Filter to relevant state
    state_income_tax_brackets = state_income_tax_brackets[state_income_tax_brackets["state"]==state]
    if itemized_deduction_amount is None:
        federal_standard_deduction = federal_income_tax_brackets["standard_deduction"].values[0]
        if state == "Utah":
            state_standard_deduction = 0
            state_tax_credit = state_income_tax_brackets["standard_deduction"].values[0]
        else:
            state_standard_deduction = state_income_tax_brackets["standard_deduction"].values[0]
            state_tax_credit = 0
    else:
        federal_standard_deduction = itemized_deduction_amount
        if state == "Utah":
            state_standard_deduction = 0
            state_tax_credit = itemized_deduction_amount
        else:
            state_standard_deduction = itemized_deduction_amount
            state_tax_credit = 0

    # Remove standard deduction from taxable income
    income_less_fed_std_deduction = income - federal_standard_deduction
    income_less_state_std_deduction = income - state_standard_deduction

    tax_total = 0
    # Federal Income Tax
    for _, row in federal_income_tax_brackets.iterrows():
        if (row['start'] <= income_less_fed_std_deduction) and (income_less_fed_std_deduction < row['end']):
            tax_total += (income_less_fed_std_deduction - row['start'])*row['tax_rate']
        elif (row['start'] <= income_less_fed_std_deduction):
            tax_total += (row['end'] - row['start'])*row['tax_rate']
    # State Income Tax
    for _, row in state_income_tax_brackets.iterrows():
        if (row['start'] <= income_less_state_std_deduction) and (income_less_state_std_deduction < row['end']):
            tax_total += (income_less_state_std_deduction - row['start'])*row['tax_rate']
        elif (row['start'] <= income_less_state_std_deduction):
            tax_total += (row['end'] - row['start'])*row['tax_rate']
    return tax_total - state_tax_credit


def calculate_capital_gains_tax_amount(income, amount_to_be_taxed_on, state, filing_status):
    cap_gains_tax = 0
    if state == "Washington" and amount_to_be_taxed_on > 250000:
        cap_gains_tax += (amount_to_be_taxed_on-250000)*0.07
    if filing_status == "Single":
        if 40400 < income and income <= 445850:
            cap_gains_tax += amount_to_be_taxed_on*0.15
        if income > 445850:
            cap_gains_tax += amount_to_be_taxed_on*0.2
    else:
        if 80800 < income and income <= 501600:
            cap_gains_tax += amount_to_be_taxed_on*0.15
        if income > 501600:
            cap_gains_tax += amount_to_be_taxed_on*0.2
    return cap_gains_tax

# Itemized tax writeoffs should only be used if its greater than the standard deduction of around $12,500
# You can deduct the mortgage interest you paid during the tax year on the first $750,000 of your mortgage debt.
# Notes: PMI is also deductable, write 750K applies to interest+prinicipal or just principal (I think it's total amount you owe), appl
def calculate_loan_interest_tax_writeoff(loan_amount, interest_paid):
     loan_ceiling = 750000
     loan_proportion = min(loan_ceiling/loan_amount, 1)
     total_interest_to_write_off = interest_paid*loan_proportion
     return total_interest_to_write_off

# You can deduct a maximum of 10,000 in property taxes
def calculate_property_tax_writeoff(property_tax_owed):
     annual_prop_tax_writeoff_ceiling = 10000
     return min(property_tax_owed, annual_prop_tax_writeoff_ceiling)