from operator import index
from unicodedata import name
import streamlit as st
import pandas as pd
import numpy as np

from tax_calculation import MAX_INT, property_tax_values, calculate_income_tax_amount, calculate_capital_gains_tax_amount, calculate_loan_interest_tax_writeoff, calculate_property_tax_writeoff

st.title("Should I Buy a House Calculator")

house_value = st.number_input(
     "What is the value of the house (in dollars)?",
     min_value=0, max_value=MAX_INT, value=600000)

downpayment_percent = st.number_input(
     "What is the percentage of your downpayment for the house?",
     min_value=0.0, max_value=100.0, value=20.0)
downpayment_percent = downpayment_percent/100

downpayment = downpayment_percent*house_value
loan_principal = house_value - downpayment

loan_interest_rate = st.number_input(
     "What is the annual interest rate percentage on the loan (assuming fixed)?",
     min_value=0.0, max_value=100.0, value=6.0)
loan_interest_rate = loan_interest_rate/100

loan_length = st.number_input(
     "How long is the loan for (in years)?",
     min_value=0, max_value=100, value=30)

pmi = st.number_input(
     "What is the primary mortgage insurance (PMI) rate percentage for this loan per year (you stop paying PMI after getting 20 percent of your principle payed off)?",
     min_value=0.0, max_value=100.0, value=1.0)
pmi = pmi/100

homeowners_insurance_amount = st.number_input(
     "How much in homeowners insurance do you owe per year (default is .35 percent of the value of the house per year)?",
     min_value=0, max_value=10000, value=int(house_value*0.0035))

annual_growth_house = st.number_input(
     "What is your estimated annual growth percentage in the home value (calculations assume rent costs rise at this rate as well)?",
     min_value=0.0, max_value=100.0, value=5.0)
annual_growth_house = annual_growth_house/100

annual_growth_invest = st.number_input(
     "What is your estimated annual growth percentage by investing your money in the market?",
     min_value=0.0, max_value=100.0, value=5.0)
annual_growth_invest = annual_growth_invest/100

monthly_rent_cost = st.number_input(
     "What is your monthly cost in rent if you were to rent instead of buy?",
     min_value=0, max_value=MAX_INT, value=2000)

monthly_rent_income = st.number_input(
     "How much rent per month would you make from renting out extra rooms if you bought your house?",
     min_value=0, max_value=MAX_INT, value=0)

time_period_evaluating = st.number_input(
     "Up to  what year would you like to investigate your wealth?",
     min_value=0, max_value=MAX_INT, value=10)

house_state = st.selectbox(
     "What state is the house in?",
     sorted(property_tax_values.columns.tolist()),
     index=0
     )

annual_income = st.number_input(
     "What is your annual income?",
     min_value=0, max_value=MAX_INT, value=100000)

filing_status = st.radio(
     "How will you be filing your taxes?",
     ["Single", "Married"], index=0)
if filing_status=='Married':
     house_sale_write_off_amount = 500000
else:
     house_sale_write_off_amount = 250000

monthly_interest_rate = loan_interest_rate/12
months_till_fully_paid = 12*loan_length
monthly_mortgage_cost = loan_principal*(monthly_interest_rate*(1 + monthly_interest_rate)**months_till_fully_paid)/((1 + monthly_interest_rate)**months_till_fully_paid - 1)
total_amount_owed_on_loan = loan_length*12*monthly_mortgage_cost

annual_property_tax = property_tax_values[house_state].values[0]*0.01*house_value

# How much you would save per month if you rented instead of buying
monthly_income_from_renting_vs_buying = ((monthly_mortgage_cost + annual_property_tax/12) - monthly_rent_income) - monthly_rent_cost

new_house_value = house_value
new_monthly_rent_income = monthly_rent_income
total_tenant_rent_paid = 0
total_property_taxes_paid = 0
total_homeowners_insurance_paid = 0
total_principle_payed_so_far = 0
total_interest_payed_so_far = 0
total_pmi_payed = 0
total_loan_interest_to_write_off = 0
total_property_tax_to_write_off = 0
total_income_tax_owed_if_buying = 0

total_income_tax_owed_if_renting = 0

new_monthly_rent_cost = monthly_rent_cost
total_value_in_saved_rent_with_investing = 0
total_rent_paid = 0

total_diff_in_rent_vs_buy = 0
total_diff_in_buy_vs_rent = 0
total_diff_in_annual_take_home_income_if_you_rent = 0
total_diff_in_annual_take_home_income_if_you_buy = 0
total_rent_vs_buy_gains = 0
total_buy_vs_rent_gains = 0

annual_take_home_income_if_you_rent = 0
annual_take_home_income_if_you_buy = 0

# Money you have if choosing to purchase house
buying_house_output_data = pd.DataFrame()
for i in range(1,time_period_evaluating+1):
     # Calculate amount of interest and principle payed off so far
     interest_paid_this_year = 0
     principal_paid_this_year = 0
     for m in range(0, 12):
          interest_payment_this_month = (loan_principal - total_principle_payed_so_far)*monthly_interest_rate
          principle_payment_this_month = monthly_mortgage_cost - interest_payment_this_month
          interest_paid_this_year += interest_payment_this_month
          principal_paid_this_year += principle_payment_this_month
          total_interest_payed_so_far += interest_payment_this_month
          total_principle_payed_so_far += principle_payment_this_month
          # If you've payed less than 20% of the principle on the loan, add PMI cost (which is about 0.1% – 2% of your loan amount per year)
          if total_principle_payed_so_far+downpayment < 0.2*house_value:
               total_pmi_payed += pmi*loan_principal

     # Mortgages will always be in full years, so we don't have to worry about edge case with a mortgage lasting 10.5 years.
     total_mortgage_paid =  monthly_mortgage_cost*12*i
     if total_mortgage_paid > total_amount_owed_on_loan:
          total_mortgage_paid = total_amount_owed_on_loan
     total_mortgage_left =  total_amount_owed_on_loan - total_mortgage_paid

     total_tenant_rent_paid += 12*new_monthly_rent_income
     total_property_taxes_paid += ((1+annual_growth_house)**(i-1))*annual_property_tax
     total_homeowners_insurance_paid += ((1+annual_growth_house)**(i-1))*homeowners_insurance_amount

     loan_interest_to_write_off = calculate_loan_interest_tax_writeoff(loan_principal, interest_paid_this_year)
     property_tax_to_write_off = calculate_property_tax_writeoff(((1+annual_growth_house)**(i-1))*annual_property_tax)
     total_loan_interest_to_write_off += loan_interest_to_write_off
     total_property_tax_to_write_off += property_tax_to_write_off

     # Calculations for if you didn't buy your house and rented instead
     total_rent_paid += new_monthly_rent_cost*12
     value_of_downpayment_with_investing = downpayment*(1+annual_growth_invest)**i

     # Calculate taxes for if you were to buy a house. You can write off a certain amount of gains from your house sale (shown below)
     annual_income_tax_owed_if_buying = calculate_income_tax_amount(annual_income+12*new_monthly_rent_income, house_state, filing_status, loan_interest_to_write_off+property_tax_to_write_off)
     capital_gains_tax_if_buying = calculate_capital_gains_tax_amount(annual_income, max((new_house_value-house_value) - house_sale_write_off_amount, 0) + total_buy_vs_rent_gains, house_state, filing_status)
     total_income_tax_owed_if_buying += annual_income_tax_owed_if_buying

     # Calculate taxes for if you were to rent a house
     annual_income_tax_owed_if_renting = calculate_income_tax_amount(annual_income, house_state, filing_status)
     capital_gains_tax_if_renting = calculate_capital_gains_tax_amount(annual_income, total_rent_vs_buy_gains + value_of_downpayment_with_investing - downpayment, house_state, filing_status)
     total_income_tax_owed_if_renting += annual_income_tax_owed_if_renting

     # New values with appreciation of property
     new_house_value = house_value*(1+annual_growth_house)**i
     new_monthly_rent_income = monthly_rent_income*(1+annual_growth_house)**i
     new_monthly_rent_cost = monthly_rent_cost*(1+annual_growth_house)**i
     
     total_rent_vs_buy_gains = total_diff_in_rent_vs_buy - total_diff_in_annual_take_home_income_if_you_rent
     total_buy_vs_rent_gains = total_diff_in_buy_vs_rent - total_diff_in_annual_take_home_income_if_you_buy

     annual_take_home_income_if_you_rent = annual_income - new_monthly_rent_cost*12 - annual_income_tax_owed_if_renting
     annual_take_home_income_if_you_buy = annual_income - interest_paid_this_year - principal_paid_this_year - annual_income_tax_owed_if_buying + 12*new_monthly_rent_income - ((1+annual_growth_house)**(i-1))*annual_property_tax - ((1+annual_growth_house)**(i-1))*homeowners_insurance_amount

     if annual_take_home_income_if_you_rent > annual_take_home_income_if_you_buy:
          annual_diff_in_take_home_income_to_invest = annual_take_home_income_if_you_rent - annual_take_home_income_if_you_buy
          total_diff_in_rent_vs_buy = (total_diff_in_rent_vs_buy + annual_diff_in_take_home_income_to_invest)*(1+annual_growth_invest)
          total_diff_in_buy_vs_rent = total_diff_in_buy_vs_rent*(1+annual_growth_invest)
          total_diff_in_annual_take_home_income_if_you_rent += annual_diff_in_take_home_income_to_invest
     else:
          annual_diff_in_take_home_income_to_invest = annual_take_home_income_if_you_buy - annual_take_home_income_if_you_rent
          total_diff_in_buy_vs_rent = (total_diff_in_buy_vs_rent + annual_diff_in_take_home_income_to_invest)*(1+annual_growth_invest)
          total_diff_in_rent_vs_buy = total_diff_in_rent_vs_buy*(1+annual_growth_invest)
          total_diff_in_annual_take_home_income_if_you_buy += annual_diff_in_take_home_income_to_invest

     buying_house_output_data = pd.concat([
          buying_house_output_data, 
          pd.DataFrame({
          'year': [i],
          'total_downpayment': [downpayment],
          'total_property_taxes_paid': [total_property_taxes_paid],
          'total_homeowners_insurance_paid': [total_homeowners_insurance_paid],
          'total_pmi_payed': [total_pmi_payed],
          'total_tenant_rent_paid': [total_tenant_rent_paid],
          'new_house_value': [new_house_value], 
          'total_house_appreciation': [new_house_value-house_value],
          'total_mortgage_paid': [total_mortgage_paid],
          'total_mortgage_left': [total_mortgage_left],
          'total_principle_payed_so_far': [total_principle_payed_so_far],
          'total_interest_payed_so_far': [total_interest_payed_so_far],
          'total_loan_interest_to_write_off': [total_loan_interest_to_write_off],
          'total_property_tax_to_write_off': [total_property_tax_to_write_off],
          'total_income_tax_owed_if_buying': [total_income_tax_owed_if_buying],
          'total_income_tax_owed_if_renting': [total_income_tax_owed_if_renting],
          'total_capital_gains_tax_owed_if_buying': [capital_gains_tax_if_buying],
          'total_capital_gains_tax_owed_if_renting': [capital_gains_tax_if_renting],
          })
     ])

net_worth_if_renting = value_of_downpayment_with_investing + total_rent_vs_buy_gains + annual_income*time_period_evaluating - total_rent_paid - capital_gains_tax_if_renting - total_income_tax_owed_if_renting
net_worth_if_buying = new_house_value + total_buy_vs_rent_gains + total_tenant_rent_paid + annual_income*time_period_evaluating - downpayment - total_amount_owed_on_loan - capital_gains_tax_if_buying - total_income_tax_owed_if_buying - total_property_taxes_paid - total_homeowners_insurance_paid

st.title(f"Net worth")
st.markdown(f"If you buy a house, your net worth after {time_period_evaluating} years will be {'${:,.2f}'.format(net_worth_if_buying)}.")
st.markdown(f"If you rent a house, your net worth after {time_period_evaluating} years will be {'${:,.2f}'.format(net_worth_if_renting)}.")

st.title(f"Buying a house")
st.markdown(f"- House value: {'${:,.2f}'.format(new_house_value)}.")
st.markdown(f"- Total mortgage cost: {'${:,.2f}'.format(total_amount_owed_on_loan)}.")
st.markdown(f"- Gains from difference in annual income: {'${:,.2f}'.format(total_buy_vs_rent_gains)}.")
st.markdown(f"- Income from tenant rent: {'${:,.2f}'.format(total_tenant_rent_paid)}.")
st.markdown(f"- Income taxes: {'${:,.2f}'.format(total_income_tax_owed_if_buying)}.")
st.markdown(f"- Capital gains taxes: {'${:,.2f}'.format(capital_gains_tax_if_buying)}.")


st.title(f"Renting a house")
st.markdown(f"- Downpayment value: {'${:,.2f}'.format(value_of_downpayment_with_investing)}.")
st.markdown(f"- Total rent paid: {'${:,.2f}'.format(total_rent_paid)}.")
st.markdown(f"- Gains from difference in annual income: {'${:,.2f}'.format(total_rent_vs_buy_gains)}.")
st.markdown(f"- Income taxes: {'${:,.2f}'.format(total_income_tax_owed_if_renting)}.")
st.markdown(f"- Capital gains taxes: {'${:,.2f}'.format(capital_gains_tax_if_renting)}.")


st.table(data=buying_house_output_data.set_index('year').style.format("${:,.2f}"))

# st.download_button(
#      label="Download data as CSV",
#      data=buying_house_output_data.set_index('year').to_csv().encode('utf-8'),
#      file_name='real_estate_cash_flow_over_time.csv',
#      mime='text/csv',
# )

# net_assets_left_when_buying = buying_house_output_data.tail(1)['new_house_value'].values[0] - buying_house_output_data.tail(1)['total_mortgage_left'].values[0] + buying_house_output_data.tail(1)['total_tenant_rent_paid'].values[0]
# net_costs_payed_when_buying = downpayment + buying_house_output_data.tail(1)['total_property_taxes_paid'].values[0] + buying_house_output_data.tail(1)['total_homeowners_insurance_paid'].values[0] + buying_house_output_data.tail(1)['total_pmi_payed'].values[0] + buying_house_output_data.tail(1)['total_mortgage_paid'].values[0]

# st.subheader(f"Net Assets: ${net_assets_left_when_buying:,.2f}")
# st.markdown(f"- Includes the {'${:,.2f}'.format(buying_house_output_data.tail(1)['total_tenant_rent_paid'].values[0])} you made over this time from tenants paying rent")
# st.subheader(f"Net Costs: ${net_costs_payed_when_buying:,.2f}")


# st.title(f"Summary")

# st.subheader(f"Buying house")



# st.markdown(f"Net gain in assets (after capital gains tax) for buying a house is **${(net_assets_left_when_buying-net_costs_payed_when_buying-capital_gains_taxes_owed):,.2f}.**")
# st.markdown(f"- You would owe about ${capital_gains_taxes_owed:,.2f} in capital gains taxes when selling the house.")

# st.markdown(f"Your property appreciated by ${buying_house_output_data.tail(1)['total_house_appreciation'].values[0]:,.2f}.")
# st.markdown(f"You would need to pay off ${buying_house_output_data.tail(1)['total_mortgage_left'].values[0]:,.2f} on your mortgage.")

# st.markdown(f"After {time_period_evaluating} years, you could write off a total of ${(total_loan_to_writeoff + total_property_tax_writeoff):,.2f} from property and mortgage interest taxes.")

# st.subheader(f"Renting house")

# st.markdown(f"Net gain in assets (not including investment capital gains and income taxes) when renting a house is **${(net_assets_left_when_renting-net_costs_payed_when_renting):,.2f}**.")
# st.markdown(f"You invested a total of {'${:,.2f}'.format(time_period_evaluating*12*monthly_income_from_renting_vs_buying+downpayment)} over {time_period_evaluating} years.")
# st.markdown(f"- {'${:,.2f}'.format(downpayment)} was from your downpayment.")
# st.markdown(f"- The remaining was from saving {'${:,.2f}'.format(monthly_income_from_renting_vs_buying)} per month if you rented instead of bought a house.")

# st.markdown(f"Using standard deduction, after {time_period_evaluating} years, you could write off a total of ${(25100*time_period_evaluating if is_married else 12550*time_period_evaluating):,.2f}.")