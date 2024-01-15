import numpy as np

def vogels_approximation_method(costs, supply, demand):
    costs_copy = costs.copy()
    n, m = costs_copy.shape

    allocation = np.zeros((n, m))

    # Set the costs of exhausted supply points to infinity
    for i, s in enumerate(supply):
        if s == 0:
            costs_copy[i, :] = float('inf')

    while np.any(supply) and np.any(demand):
        # Calculate row and column penalties (differences)
        row_diffs = []
        col_diffs = []

        # For rows
        for i, row in enumerate(costs_copy):
            sorted_row = sorted([c for c in row if c != float('inf')])
            if len(sorted_row) > 1:
                row_diffs.append(sorted_row[1] - sorted_row[0])
            else:
                row_diffs.append(0)

        # For columns
        for j, col in enumerate(costs_copy.T):
            sorted_col = sorted([c for c in col if c != float('inf')])
            if len(sorted_col) > 1:
                col_diffs.append(sorted_col[1] - sorted_col[0])
            else:
                col_diffs.append(0)

        # If all differences are 0, break
        if all(diff == 0 for diff in row_diffs) and all(diff == 0 for diff in col_diffs):
            break

        # Determine the highest penalty
        max_row_diff = max(row_diffs)
        max_col_diff = max(col_diffs)

        # Assign as much as possible to the highest penalty position
        if max_row_diff > max_col_diff:
            i = row_diffs.index(max_row_diff)
            j = np.argmin(costs_copy[i])
        else:
            j = col_diffs.index(max_col_diff)
            i = np.argmin(costs_copy[:, j])

        # Make the allocation
        allocated_amount = min(supply[i], demand[j])
        allocation[i][j] = allocated_amount
        supply[i] -= allocated_amount
        demand[j] -= allocated_amount

        # Set the costs of exhausted supply or demand to infinity
        if supply[i] == 0:
            costs_copy[i, :] = float('inf')
        if demand[j] == 0:
            costs_copy[:, j] = float('inf')

    # If there's any unmet demand, allocate it to the least costly supply points
    for j, d in enumerate(demand):
        if d > 0:
            i = np.argmin(costs[:, j])
            allocation[i][j] += d

    return allocation

# Q1
# Initial data
supply = np.array([22, 3.7, 4.5, 47, 18.5, 5.0])
demand = np.array([3.0, 2.60, 16.0, 20.0, 26.4, 11.90])

# Cost matrix
costs = np.array([
    [92.63, 104.03, 145.95, 112.43, 107.80, 112.19],
    [160.20, 93.25, 148.88, 113.61, 103.45, 111.85],
    [186.70, 122.31, 112.31, 135.98, 127.76, 133.35],
    [127.34, 84.84, 122.51, 73.34, 87.84, 91.04],
    [152.64, 95.15, 144.73, 107.62, 89.15, 107.00],
    [252.78, 162.24, 236.36, 177.62, 168.96, 149.24]
])

# Q2
# Original scenario
allocation_result = vogels_approximation_method(costs, supply.copy(), demand.copy())
print(allocation_result)
total_cost = np.sum(allocation_result * costs / 100)
print("Total cost is:", total_cost)

# Q3
#Calculate cost saved from the team plan
team_cost = 78.445
cost_saved = team_cost - total_cost
print("Cost save is", cost_saved)

# Q4
# 85% supply scenario
supply_85 = 0.85 * supply
allocation_result_85 = vogels_approximation_method(costs, supply_85.copy(), demand.copy())
print(allocation_result_85)
total_cost_85 = np.sum(allocation_result_85 * costs / 100)
print("Total cost of 85% capacity is:", total_cost_85)
more_costly = total_cost_85 - total_cost
print("More costly with the 85% capacity is", more_costly)

# Q5
# No Chile capacity scenario
supply_NoChile = 0.9 * np.array([22, 3.7, 0, 47, 18.5, 5.0])
allocation_result_NoChile = vogels_approximation_method(costs, supply_NoChile.copy(), demand.copy())
print(allocation_result_NoChile)
total_cost_NoChile = np.sum(allocation_result_NoChile * costs / 100)
print("Total cost without Chile capacity is:", total_cost_NoChile)

# Cost Comparison
print("The team cost is", team_cost)
print("Our plan cost is", total_cost)
print("Our plan with 85% capacity is", total_cost_85)
print("Our plan without Chile is", total_cost_NoChile)