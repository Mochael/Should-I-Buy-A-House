from operator import index
from unicodedata import name
import streamlit as st
import pandas as pd
import numpy as np

MAX_INT = 1000000000000000

st.title("Should I Buy a House Calculator")


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

house_value = st.number_input(
     "What is the value of the house (in dollars)?",
     min_value=0, max_value=MAX_INT, value=1000000)

downpayment_percent = st.number_input(
     "What is the proportion of your downpayment for the house?",
     min_value=0.0, max_value=1.0, value=0.2)

downpayment = downpayment_percent*house_value
loan_principal = house_value - downpayment

loan_interest_rate = st.number_input(
     "What is the annual interest rate on the loan (assuming fixed)?",
     min_value=0.0, max_value=1.0, value=0.04)

loan_length = st.number_input(
     "How long is the loan for (in years)?",
     min_value=0, max_value=100, value=15)

pmi = st.number_input(
     "What is the primary mortgage insurance (PMI) rate for this loan per year (you stop paying PMI after getting 20 percent of your principle payed off)?",
     min_value=0.0, max_value=1.0, value=0.01)

homeowners_insurance_amount = st.number_input(
     "How much in homeowners insurance do you owe per year (default is .35 percent of the value of the house per year)?",
     min_value=0, max_value=10000, value=int(house_value*0.0035))

annual_growth_house = st.number_input(
     "What is your estimated annual growth in the home value?",
     min_value=0.0, max_value=100.0, value=0.055)

annual_growth_invest = st.number_input(
     "What is your estimated annual growth by investing your money in the market?",
     min_value=0.0, max_value=100.0, value=0.1)

monthly_rent_cost = st.number_input(
     "What is your monthly cost in rent if you were to rent instead of buy?",
     min_value=0, max_value=MAX_INT, value=2000)

monthly_rent_income = st.number_input(
     "How much rent per month would you make from additional tenants?",
     min_value=0, max_value=MAX_INT, value=2000)

time_period_evaluating = st.number_input(
     "Up to  what year would you like to investigate your profit?",
     min_value=0, max_value=MAX_INT, value=10)

monthly_interest_rate = loan_interest_rate/12
months_till_fully_paid = 12*loan_length
monthly_mortgage_cost = loan_principal*(monthly_interest_rate*(1 + monthly_interest_rate)**months_till_fully_paid)/((1 + monthly_interest_rate)**months_till_fully_paid - 1)

total_amount_owed_on_loan = loan_length*12*monthly_mortgage_cost

house_state = st.radio(
     "What state is the house in?",
     property_tax_values.columns.tolist(), index=0)

is_married = st.radio(
     "Are you married?",
     ['Yes', 'No'], index=1)


# Itemized tax writeoffs should only be used if its greater than the standard deduction of around $12,500
def calculate_loan_interest_tax_writeoff(loan_amount, loan_amount_with_interest, loan_length, time_period_evaluating):
     loan_ceiling = 750000
     loan_proportion = min(loan_ceiling/loan_amount, 1)
     total_interest_to_write_off = (loan_amount_with_interest - loan_amount)*min(time_period_evaluating/loan_length, loan_proportion)
     return total_interest_to_write_off

def calculate_property_tax_writeoff(property_tax_owed, time_period_evaluating):
     annual_prop_tax_writeoff_ceiling = 10000
     return min(property_tax_owed, annual_prop_tax_writeoff_ceiling)*time_period_evaluating

total_loan_to_writeoff = calculate_loan_interest_tax_writeoff(loan_principal, total_amount_owed_on_loan, loan_length, time_period_evaluating)

annual_property_tax = property_tax_values[house_state].values[0]*0.01*house_value
total_property_tax_writeoff = calculate_property_tax_writeoff(annual_property_tax, time_period_evaluating)

# How much you would save per month if you rented instead of buying
monthly_income_from_renting_vs_buying = ((monthly_mortgage_cost + annual_property_tax/12) - monthly_rent_income) - monthly_rent_cost

total_tenant_rent_paid = 0
total_property_taxes_paid = 0
total_homeowners_insurance_paid = 0
principle_payed_so_far = 0
interest_payed_so_far = 0
total_pmi_payed = 0

# Money you have if choosing to purchase house
buying_house_output_data = pd.DataFrame()
for i in range(1,time_period_evaluating+1):
     new_house_value = house_value*(1+annual_growth_house)**i
     new_monthly_rent_income = monthly_rent_income*(1+annual_growth_house)**(i-1)
     mortgage_paid =  monthly_mortgage_cost*12*i
     if mortgage_paid > total_amount_owed_on_loan:
          mortgage_paid = total_amount_owed_on_loan
     mortgage_left =  total_amount_owed_on_loan - mortgage_paid
     total_tenant_rent_paid += ((1+annual_growth_house)**i)*12*new_monthly_rent_income
     total_property_taxes_paid += ((1+annual_growth_house)**i)*annual_property_tax
     total_homeowners_insurance_paid += ((1+annual_growth_house)**i)*homeowners_insurance_amount
     # If you've payed less than 20% of the principle on the loan, add PMI cost
     if principle_payed_so_far+downpayment < 0.2*house_value:
          total_pmi_payed += pmi*loan_principal

     # Calculate amount of interest and principle payed off so far
     for m in range(0, 12):
          interest_payment_this_month = (loan_principal - principle_payed_so_far)*monthly_interest_rate
          principle_payment_this_month = monthly_mortgage_cost - interest_payment_this_month
          principle_payed_so_far += principle_payment_this_month
          interest_payed_so_far += interest_payment_this_month

     buying_house_output_data = buying_house_output_data.append(pd.DataFrame({
        'year': [i],
        'total_downpayment': [downpayment],
        'total_property_taxes_paid': [total_property_taxes_paid],
        'total_homeowners_insurance_paid': [total_homeowners_insurance_paid],
        'total_pmi_payed': [total_pmi_payed],
        'total_tenant_rent_paid': [total_tenant_rent_paid],
        'new_house_value': [new_house_value], 
        'total_house_appreciation': [new_house_value-house_value],
        'total_mortgage_paid': [mortgage_paid],
        'total_mortgage_left': [mortgage_left],
        'principle_payed_so_far': [principle_payed_so_far],
        'interest_payed_so_far': [interest_payed_so_far]
        }))
        
st.title(f"Buying a house")

st.markdown(f"You owe {'${:,.2f}'.format(total_amount_owed_on_loan)} on your loan over {loan_length} years.")
st.markdown(f"- This is {'${:,.2f}'.format(monthly_mortgage_cost)} per month")

st.table(data=buying_house_output_data.set_index('year').style.format("${:,.2f}"))

net_assets_left_when_buying = buying_house_output_data.tail(1)['new_house_value'].values[0] - buying_house_output_data.tail(1)['total_mortgage_left'].values[0]
net_costs_payed_when_buying = downpayment + buying_house_output_data.tail(1)['total_property_taxes_paid'].values[0] + buying_house_output_data.tail(1)['total_homeowners_insurance_paid'].values[0] + buying_house_output_data.tail(1)['total_pmi_payed'].values[0] + buying_house_output_data.tail(1)['total_mortgage_paid'].values[0] - buying_house_output_data.tail(1)['total_tenant_rent_paid'].values[0]

st.subheader(f"Net Assets: ${net_assets_left_when_buying:,.2f}")
st.subheader(f"Net Costs: ${net_costs_payed_when_buying:,.2f}")


st.title(f"Renting houses")

# Money you have if choosing to rent
total_value_in_saved_rent_with_investing = 0
renting_house_output_data = pd.DataFrame()
for i in range(1,time_period_evaluating+1):
     new_monthly_rent_cost = monthly_rent_cost*(1+annual_growth_house)**(i-1)
     total_rent_paid = new_monthly_rent_cost*12*i
     value_of_downpayment_with_investing = downpayment*(1+annual_growth_invest)**i
     total_in_saved_property_expenses = monthly_income_from_renting_vs_buying*12*i
     this_year_accumulated_monthly_investment_gains = 0
     for month in range(12):
          this_year_accumulated_monthly_investment_gains += monthly_income_from_renting_vs_buying*(1+(annual_growth_invest*month)/12)
     total_value_in_saved_rent_with_investing = this_year_accumulated_monthly_investment_gains + total_value_in_saved_rent_with_investing*(1+annual_growth_invest)
     
     renting_house_output_data = renting_house_output_data.append(pd.DataFrame({
          'year': [i],
          'total_rent_paid': [total_rent_paid],
          'total_in_saved_property_expenses': [total_in_saved_property_expenses],
          'value_of_downpayment_with_investing': [value_of_downpayment_with_investing],
          'total_value_in_saved_rent_with_investing': [total_value_in_saved_rent_with_investing],
          }))

st.table(data=renting_house_output_data.set_index('year').style.format("${:,.2f}"))

net_assets_left_when_renting = renting_house_output_data.tail(1)['value_of_downpayment_with_investing'].values[0] + renting_house_output_data.tail(1)['total_value_in_saved_rent_with_investing'].values[0]
net_costs_payed_when_renting = renting_house_output_data.tail(1)['total_rent_paid'].values[0]

st.subheader(f"Net Assets: ${net_assets_left_when_renting:,.2f}")
st.subheader(f"Net Costs: ${net_costs_payed_when_renting:,.2f}")

def calculate_capital_gains_taxes(number, married):
     # Assuming income is above 41,675 (if single) or 83,350 (if married) threshold for 0% tax
     # thresh_1 = 41675
     thresh_2 = 459750
     if married:
          # thresh_1 = 83350
          thresh_2 = 517200
     taxes_owed = 0
     if number > thresh_2:
          taxes_owed += 0.2*(number-thresh_2)
          number = thresh_2
     # if number > thresh_1:
          # taxes_owed += 0.15*(number-thresh_1)    
     taxes_owed += 0.15*number     
     return taxes_owed

st.title(f"Summary")

st.subheader(f"Buying house")

if is_married=='Yes':
     house_sale_write_off_amount = min(buying_house_output_data.tail(1)['total_house_appreciation'].values[0], 500000)
else:
     house_sale_write_off_amount = min(buying_house_output_data.tail(1)['total_house_appreciation'].values[0], 250000)
capital_gains_taxes_owed = calculate_capital_gains_taxes(buying_house_output_data.tail(1)['total_house_appreciation'].values[0]-house_sale_write_off_amount, is_married)

st.markdown(f"Net gain in assets (after capital gains tax) for buying a house is ${(net_assets_left_when_buying-net_costs_payed_when_buying-capital_gains_taxes_owed):,.2f}.")
st.markdown(f"- You would owe about ${capital_gains_taxes_owed:,.2f} in capital gains taxes when selling the house.")

st.markdown(f"Your property appreciated by ${buying_house_output_data.tail(1)['total_house_appreciation'].values[0]:,.2f}.")
st.markdown(f"You would need to pay off ${buying_house_output_data.tail(1)['total_mortgage_left'].values[0]:,.2f} on your mortgage.")

st.markdown(f"After {time_period_evaluating} years, you could write off a total of ${(total_loan_to_writeoff + total_property_tax_writeoff):,.2f} from property and mortgage interest taxes.")

st.subheader(f"Renting house")

st.markdown(f"Net gain in assets (not including investment capital gains and income taxes) when renting a house is ${(net_assets_left_when_renting-net_costs_payed_when_renting):,.2f}.")
st.markdown(f"You invested a total of {'${:,.2f}'.format(time_period_evaluating*12*monthly_income_from_renting_vs_buying+downpayment)} over {time_period_evaluating} years.")
st.markdown(f"- {'${:,.2f}'.format(downpayment)} was from your downpayment.")
st.markdown(f"- The remaining was from saving {'${:,.2f}'.format(monthly_income_from_renting_vs_buying)} per month if you rented instead of bought a house.")

st.markdown(f"Using standard deduction, after {time_period_evaluating} years, you could write off a total of ${(25100*time_period_evaluating if is_married else 12550*time_period_evaluating):,.2f}.")