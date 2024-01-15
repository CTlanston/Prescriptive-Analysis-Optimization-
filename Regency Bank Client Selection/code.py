#%%
import numpy as np
import pandas as pd

# Constants for the simulation model
fixed_migration_cost = 500000
migration_cost_per_account = {1: 2000, 2: 5000, 3: 7000}
fixed_operating_cost = 200000
operating_cost_per_account = {1: 1500, 2: 2000, 3: 3000}
cost_to_issue_card = 45
annual_cost_to_service_card = 40
attrition_rate = 0.10
risk_of_default = {7: 0.10, 6: 0.05, 5: 0.03, 4: 0.02, 3: 0.01, 2: 0.005, 1: 0.001}
months_of_charges_written_off = {7: 6, 6: 4, 5: 3, 4: 3, 3: 3, 2: 3, 1: 3}
annual_spend_growth_rate = 0.08
number_of_cards_growth_rate = 0.10
growth_rate_std_dev = 0.01
simulation_iterations = 1000


#%%
# Load the full client dataset
client_data_path = "C:\\Users\\Dola\\Downloads\\RegencyClientList.xlsx"
df = pd.read_excel(client_data_path)

#%%
# Function to run the simulation
def simulate_client_portfolio(df, iterations):
    results_df = pd.DataFrame(index=range(iterations), columns=['Total Revenue', 'Total Cost', 'Net Revenue'])

    for iteration in range(iterations):
        df_sim = df.copy()
        total_revenue = 0
        total_cost = fixed_migration_cost  # Fixed migration cost added once

        # For the first year, calculate card issue costs for all cards
        df_sim['Card Issue Costs'] = df_sim['# of Cards'] * cost_to_issue_card
        total_cost += df_sim['Card Issue Costs'].sum()

        for year in range(1, 4):  # Simulate over 3 years
            total_cost += fixed_operating_cost  # Add fixed operating cost for the year

            if year > 1:
                # Apply individual growth rates for each account's number of cards
                df_sim['Card Growth'] = np.random.normal(number_of_cards_growth_rate, growth_rate_std_dev, len(df_sim))

                # Calculate potential new cards, ensuring no reduction in existing cards
                potential_new_cards = (df_sim['# of Cards'] * (1 + df_sim['Card Growth'])).apply(np.floor)
                df_sim['New Cards'] = (potential_new_cards - df_sim['# of Cards']).clip(lower=0)

                # Update the number of cards and calculate issue costs for new cards only
                df_sim['# of Cards'] = potential_new_cards
                df_sim['Card Issue Costs'] = df_sim['New Cards'] * cost_to_issue_card
                total_cost += df_sim['Card Issue Costs'].sum()

            # Reset new cards count for the next iteration
            df_sim['New Cards'] = 0

            # Calculate revenue
            df_sim['Revenue'] = df_sim['Annual Spend Volume'] * 0.01 + 5000
            total_revenue += df_sim['Revenue'].sum()

            # Calculate operating costs
            df_sim['Operating Costs'] = df_sim['Complexity Level'].map(operating_cost_per_account)
            df_sim['Card Service Costs'] = df_sim['# of Cards'] * annual_cost_to_service_card
            total_cost += df_sim['Operating Costs'].sum() + df_sim['Card Service Costs'].sum()

            # Calculate potential cost of default and remove defaulted accounts
            df_sim['Default'] = np.random.rand(len(df_sim)) < df_sim['Risk Rating'].map(risk_of_default)
            df_sim['Cost of Default'] = df_sim['Default'] * df_sim['Annual Spend Volume'] * df_sim['Risk Rating'].map(months_of_charges_written_off) / 12
            total_cost += df_sim['Cost of Default'].sum()
            df_sim = df_sim[~df_sim['Default']]  # Remove defaulted accounts

            # Apply attrition to remove accounts
            attrition = np.random.rand(len(df_sim)) < attrition_rate
            df_sim = df_sim[~attrition]  # Remove attrited accounts

        # Record the results for the iteration
        results_df.loc[iteration, 'Total Revenue'] = total_revenue
        results_df.loc[iteration, 'Total Cost'] = total_cost
        results_df.loc[iteration, 'Net Revenue'] = total_revenue - total_cost

    return results_df


# %%
simulation_results = simulate_client_portfolio(df, simulation_iterations)
# %%
simulation_results

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# %%
risk_rating_combinations = [
    [1],
    [1, 2],
    [1, 2, 3],
    [1, 2, 3, 4],
    [1, 2, 3, 4, 5],
    [1, 2, 3, 4, 5, 6],
    [1, 2, 3, 4, 5, 6, 7]]
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# Suppress specific FutureWarnings from seaborn
warnings.filterwarnings('ignore', category=FutureWarning, module='seaborn')

# Initialize a dictionary to store results for each combination
detailed_results = {}

# Iterate over each risk level combination
for combination in risk_rating_combinations:
    filtered_df = df[df['Risk Rating'].isin(combination)].copy()
    
    # Run your simulation for the combination
    simulation_results = simulate_client_portfolio(filtered_df, simulation_iterations)
    
    # Extract 'Total Revenue' and 'Net Revenue' from simulation results
    total_revenues = simulation_results['Total Revenue']
    net_revenues = simulation_results['Net Revenue']
    
    detailed_results[str(combination)] = {
        'Total Revenue': total_revenues,
        'Net Revenue': net_revenues
    }

#%%
# Iterate over the results and plot distributions
for combination, metrics in detailed_results.items():
    print(f"Combination: {combination}")
    stats_df = pd.DataFrame({metric: [np.max(values), np.min(values), np.std(values), np.median(values), np.mean(values)] 
                                    for metric, values in metrics.items()})
    stats_df.index = ['Max', 'Min', 'Std', 'Median', 'Mean']
    print(stats_df)

    # Plotting
    plt.figure(figsize=(15, 5))
    for idx, (metric, values) in enumerate(metrics.items()):
        plt.subplot(1, len(metrics), idx + 1)
        sns.histplot(values, kde=True)
        plt.title(f'{metric} Distribution')
        plt.xlabel(metric)
        plt.ylabel('Frequency')
    plt.tight_layout()
    plt.show()

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from itertools import combinations

# Define the complexity levels in your dataset
complexity_levels = [1, 2, 3]  # Modify this list according to your dataset

# Initialize a dictionary to store results for each complexity level combination
complexity_results = {}

# Iterate over all combinations of complexity levels
for num_levels in range(1, len(complexity_levels) + 1):
    level_combinations = combinations(complexity_levels, num_levels)
    for combination in level_combinations:
        # Filter the client dataset by the current combination of complexity levels
        filtered_df = df[df['Complexity Level'].isin(combination)].copy()

        # Run your simulation for the combination
        simulation_results = simulate_client_portfolio(filtered_df, simulation_iterations)
    
        # Extract 'Total Revenue' and 'Net Revenue' from simulation results
        total_revenues = simulation_results['Total Revenue']
        net_revenues = simulation_results['Net Revenue']
    
        detailed_results[str(combination)] = {
            'Net Revenue': net_revenues}

#%%
# Iterate over the results and plot distributions
for combination, metrics in detailed_results.items():
    print(f"Combination: {combination}")
    stats_df = pd.DataFrame({metric: [np.max(values), np.min(values), np.std(values), np.median(values), np.mean(values)] 
                                    for metric, values in metrics.items()})
    stats_df.index = ['Max', 'Min', 'Std', 'Median', 'Mean']
    print(stats_df)

    # Plotting
    plt.figure(figsize=(15, 5))
    for idx, (metric, values) in enumerate(metrics.items()):
        plt.subplot(1, len(metrics), idx + 1)
        sns.histplot(values, kde=True)
        plt.title(f'{metric} Distribution')
        plt.xlabel(metric)
        plt.ylabel('Frequency')
    plt.tight_layout()
    plt.show()

# %%
# Define percentile groups
percentile_groups = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # You can adjust the percentiles as needed

# Initialize a dictionary to store results for each percentile group
size_results = {}

# Suppress specific FutureWarnings from seaborn
warnings.filterwarnings('ignore', category=FutureWarning, module='seaborn')

# Iterate over percentile groups
for i, percentile in enumerate(percentile_groups):
    if i == 0:
        min_percentile = 0
    else:
        min_percentile = percentile_groups[i - 1]
    max_percentile = percentile_groups[i]
    
    # Filter clients within the current percentile group based on annual spend volume
    min_spend = np.percentile(df['Annual Spend Volume'], min_percentile)
    max_spend = np.percentile(df['Annual Spend Volume'], max_percentile)
    filtered_df = df[(df['Annual Spend Volume'] >= min_spend) & (df['Annual Spend Volume'] <= max_spend)].copy()
    
    # Run your simulation for the filtered group
    results = simulate_client_portfolio(filtered_df, simulation_iterations)
    
    # Extract the required metrics
    Net_revenues = results['Net Revenue']
    
    # Store the results in the dictionary
    size_results[f'Percentile {min_percentile}-{max_percentile}'] = {
        'Net Revenue': Net_revenues
    }

# Iterate over the results and plot distributions for each percentile group
for group, metrics in size_results.items():
    print(f"Group: {group}")
    stats_df = pd.DataFrame({metric: [np.max(values), np.min(values), np.std(values), np.median(values), np.mean(values)] 
                                    for metric, values in metrics.items()})
    stats_df.index = ['Max', 'Min', 'Std', 'Median', 'Mean']
    print(stats_df)

    # Plotting
    plt.figure(figsize=(15, 5))
    for idx, (metric, values) in enumerate(metrics.items()):
        plt.subplot(1, len(metrics), idx + 1)
        sns.histplot(values, kde=True)
        plt.title(f'{metric} Distribution')
        plt.xlabel(metric)
        plt.ylabel('Frequency')
    plt.tight_layout()
    plt.show()

# %%
# Define new percentile ranges
percentile_ranges = [(75, 100), (80, 100), (85, 100)]

# Initialize a dictionary to store results for each percentile range
size_results = {}

# Suppress specific FutureWarnings from seaborn
warnings.filterwarnings('ignore', category=FutureWarning, module='seaborn')

# Iterate over the defined percentile ranges
for min_percentile, max_percentile in percentile_ranges:
    
    # Filter clients within the current percentile range based on annual spend volume
    min_spend = np.percentile(df['Annual Spend Volume'], min_percentile)
    max_spend = np.percentile(df['Annual Spend Volume'], max_percentile)
    filtered_df = df[(df['Annual Spend Volume'] > min_spend) & (df['Annual Spend Volume'] <= max_spend)].copy()
    
    # Run your simulation for the filtered group
    results = simulate_client_portfolio(filtered_df, simulation_iterations)
    
    # Extract the required metrics
    Net_revenues = results['Net Revenue']
    
    # Store the results in the dictionary
    size_results[f'Percentile {min_percentile}-{max_percentile}'] = {
        'Net Revenue': Net_revenues
    }

# Iterate over the results and plot distributions for each percentile range
for group, metrics in size_results.items():
    print(f"Group: {group}")
    stats_df = pd.DataFrame({metric: [np.max(values), np.min(values), np.std(values), np.median(values), np.mean(values)] 
                                    for metric, values in metrics.items()})
    stats_df.index = ['Max', 'Min', 'Std', 'Median', 'Mean']
    print(stats_df)

    # Plotting
    plt.figure(figsize=(15, 5))
    for idx, (metric, values) in enumerate(metrics.items()):
        plt.subplot(1, len(metrics), idx + 1)
        sns.histplot(values, kde=True)
        plt.title(f'{metric} Distribution')
        plt.xlabel(metric)
        plt.ylabel('Frequency')
    plt.tight_layout()
    plt.show()


# %%
# Define the risk level range and percentile range
risk_level_range = [1, 2, 3, 4, 5]
min_percentile, max_percentile = 80, 100

# Filter clients based on the risk level range
risk_filtered_df = df[df['Risk Rating'].isin(risk_level_range)].copy()

# Filter clients within the percentile range based on annual spend volume
min_spend = np.percentile(risk_filtered_df['Annual Spend Volume'], min_percentile)
max_spend = np.percentile(risk_filtered_df['Annual Spend Volume'], max_percentile)
final_filtered_df = risk_filtered_df[(risk_filtered_df['Annual Spend Volume'] > min_spend) & (risk_filtered_df['Annual Spend Volume'] <= max_spend)].copy()

# Run your simulation for the filtered group
simulation_results = simulate_client_portfolio(final_filtered_df, simulation_iterations)

# Extract 'Net Revenue' from simulation results
net_revenues = simulation_results['Net Revenue']

# Print statistics of the net revenue
stats_df = pd.DataFrame({'Net Revenue': [np.max(net_revenues), np.min(net_revenues), np.std(net_revenues), np.median(net_revenues), np.mean(net_revenues)]})
stats_df.index = ['Max', 'Min', 'Std', 'Median', 'Mean']
print(stats_df)

# Plotting
plt.figure(figsize=(7, 5))
sns.histplot(net_revenues, kde=True)
plt.title('Net Revenue Distribution for Risk Levels 1-5 and Top 20% Clients')
plt.xlabel('Net Revenue')
plt.ylabel('Frequency')
plt.show()

# %%
