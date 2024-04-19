import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
    # Input values
st.header("DAESUNG Energy Co-Generation Optimization")
gen_kW = st.number_input("Enter gen_kWh/m3 value", value=3.63, step=0.01)
household_count = st.number_input("Enter household_count value", value=526, step=1)
effi_boil = st.number_input("Enter effi_boil value", value=0.4, step=0.01)
month = st.slider("Select month", 1, 12, 5)
# total_kWh = round(st.number_input("Enter total_kWh value", value=219342, step=1)/household_count,0)
total_kWh = round(st.number_input("Enter total_kWh value", value=219342, step=1)/household_count)
st.write(f"Total kWh per household: {total_kWh}")

heat = round(st.number_input("Enter Gas ㎥/month", value=71536, step=1)/household_count,0)

st.write(f"Total Gas m3 per household: {heat}")

# total_kWh = st.number_input("Enter total_kWh value", value=417, step=1)
# heat = st.number_input("Enter Gas ㎥/month", value=136, step=1)
# cogen_rate = 19.65 * 1.1
# boil_rate = 21.8144 * 1.1
MJ = 42.7

cogen_rate = round(st.number_input("Enter Gas cogen Won/㎥ without VAT" , value=19.65, step=0.01)*1.1,0) 
boil_rate = round(st.number_input("Enter Gas boiler Won/㎥ without VAT", value=21.8144, step=0.01)*1.1,0) 


base_rate = round(st.number_input("Enter base rate Won/kWh", value=105.0, step=0.1),0) 
seconde_rate = round(st.number_input("Enter second rate Won/kWh", value=174.0, step=0.1),0) 
third_rate = round(st.number_input("Enter third rate Won/kWh", value=242.3, step=0.1),0) 


def plot_costs(df_table, month):
    """Plots the cost analysis for a given month."""
    plt.figure(figsize=(10, 6))
    plt.plot(df_table['i'], df_table['cost_elec'], label='Electricity Cost')
    plt.plot(df_table['i'], df_table['cost_cogen'], label='Cogen Cost')
    plt.plot(df_table['i'], df_table['total'], label='Total Cost')

    # Highlight the minimum total row
    min_total_row = df_table.loc[df_table['total'].idxmin()]
    plt.axvline(x=min_total_row['i'], color='r', linestyle='--', label='Min Total')
    plt.xlabel('MWh')
    plt.ylabel('Cost(Won)')
    plt.title(f'{month}월 Co-gen Cost Analysis')
    plt.legend()
    plt.tight_layout()
    plt.show()
def fare_cogen():
    """Calculates the cogeneration fare."""

    out = round((cogen_rate * MJ) / gen_kW * 1.1, 0)
    # save_out = round((MJ * effi_boil * boil_rate) / gen_kW * 1.1, 0)

    return out


def calculate_electricity_bill(kwh, month):
    """Calculates the electricity bill for a given month and consumption."""

    summer_months = [7, 8]
    other_months = list(set(range(1, 13)) - set(summer_months))
    climate_charge_rate = 9
    fuel_cost_adjustment_rate = 5
    vat_rate = 0.1
    electric_fund_rate = 0.037



    if month in summer_months:
        if kwh <= 300:
            basic_charge = 730
            energy_charge = kwh * base_rate
        elif kwh <= 450:
            basic_charge = 1260
            energy_charge = (300 * base_rate) + ((kwh - 300) * seconde_rate)
        else:
            basic_charge = 6060
            energy_charge = (300 * base_rate) + (150 * seconde_rate) + ((kwh - 450) * third_rate)
    elif month in other_months:
        if kwh <= 200:
            basic_charge = 730
            energy_charge = kwh * base_rate
        elif kwh <= 400:
            basic_charge = 1260
            energy_charge = (200 * base_rate) + ((kwh - 200) * seconde_rate)
        else:
            basic_charge = 6060
            energy_charge = (200 * base_rate) + (200 * seconde_rate) + ((kwh - 400) * third_rate)

    climate_charge = kwh * climate_charge_rate
    fuel_cost_adjustment = kwh * fuel_cost_adjustment_rate
    total_charge = basic_charge + energy_charge + climate_charge + fuel_cost_adjustment
    vat = total_charge * vat_rate
    electric_fund = total_charge * electric_fund_rate
    final_charge = total_charge + vat + electric_fund

    return final_charge

def analyze_costs(month, gen_kW, household_count, effi_boil, total_kWh, heat):
    # Your existing analyze_costs function code here
    # Use the provided input values instead of the hard-coded values
    """Analyzes the costs for each month in the dataset."""

    data = []


    for i in range(total_kWh, 0, -1):
        heat_cogen = effi_boil / gen_kW * (total_kWh - i)
        if heat > heat_cogen:
            heat_cogen = heat_cogen
        else:
            heat_cogen = heat

        cost_cogen = fare_cogen() * (total_kWh - i)
        cost_elec = calculate_electricity_bill(i, month)
        cost_boiler = (heat-heat_cogen) * MJ * boil_rate
        total = cost_cogen + cost_elec +cost_boiler
        data.append([month, i, cost_elec, cost_cogen, cost_boiler, total, heat, heat_cogen])

    df_table = pd.DataFrame(data, columns=['month', 'i', 'cost_elec', 'cost_cogen','cost_boiler', 'total', 'heat', 'heat_cogen'])
    df_table = df_table.astype(int)

    saving = round(df_table['total'][0] - df_table['total'].min(), 0)
    columns_to_multiply = ['i', 'cost_elec', 'cost_cogen', 'cost_boiler','total', 'heat', 'heat_cogen']
    df_table2 = df_table[columns_to_multiply].apply(lambda x: x * household_count).astype(int)
    # df_table2 =df_table

    # total_savings = saving * household_count/1000
    plot_costs(df_table2, month)
   
    print(df_table2)
    min_total_row = df_table2.loc[df_table2['total'].idxmin()]
    print(min_total_row)
    # print('{:,.0f}'.format(total_savings))
    return df_table2

def main():
    st.title("Cogen Cost Analysis")


    # Run analysis when button is clicked
    if st.button("Run Analysis"):

                # Analyze costs and display results
                df_table2 = analyze_costs(month, gen_kW, household_count, effi_boil, total_kWh, heat)

                # Create the line chart
                chart = px.line(df_table2, x='i', y=['cost_elec', 'cost_cogen', 'cost_boiler', 'total'])

                # Add a vertical line at a specific point, for example, the minimum total cost
                min_total_row = df_table2.loc[df_table2['total'].idxmin()]['i']  # Get the x-coordinate of the minimum total cost
                chart.add_vline(x=min_total_row, line_dash="dash", line_color="red", annotation_text="Minimum Total Cost", annotation_position="top right")

                # Update x-axis and y-axis labels
                chart.update_xaxes(title_text='kWh')
                chart.update_yaxes(title_text='천원')

                # Display the chart
                st.plotly_chart(chart, use_container_width=True)

                st.subheader("Best Operation point")
                min_total_row = df_table2.loc[df_table2['total'].idxmin()]
                st.write(min_total_row)

                st.subheader("Cost Analysis Plot")
                analyze_costs(month, gen_kW, household_count, effi_boil, total_kWh, heat)
                st.write(df_table2)











if __name__ == "__main__":
    main()