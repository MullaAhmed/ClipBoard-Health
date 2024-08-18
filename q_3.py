import copy
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# Constants
BASELINE_FEE = 100
ORGANIC_CUSTOMERS = 25
BASE_CHURN_RATE = 0.1
CSAT_IMPROVEMENT = 1
NEW_CUSTOMERS_PER_SALESPERSON = 5
CUSTOMERS_PER_ACCOUNT_MANAGER = 25
REVENUE_INCREASE_RATE = 0.2
CSAT_CHURN_REDUCTION = 0.15
INITIAL_CUSTOMERS = 1000
INITIAL_CSAT = 70

# Function to calculate cumulative revenue
def calculate_cumulative_revenue(employee_allocation, MONTHS):
    customers = INITIAL_CUSTOMERS
    cumulative_revenue = 0
    customer_revenues = [BASELINE_FEE] * int(customers)
    customer_managed_months = [0] * int(customers)

    monthly_revenue_arr = []
    for month in range(MONTHS):
        new_business, account_managers, support = employee_allocation[month]

        # Calculate CSAT and churn rate
        csat = min(INITIAL_CSAT + (support * CSAT_IMPROVEMENT), 100)
        churn_rate = BASE_CHURN_RATE * ((1 - CSAT_CHURN_REDUCTION) ** (csat - 70))

        # Calculate new customers
        new_customers = ORGANIC_CUSTOMERS + (new_business * NEW_CUSTOMERS_PER_SALESPERSON)

        # Apply churn
        churned_customers = int(customers * churn_rate)
        customers = customers - churned_customers + int(new_customers)

        # Update customer revenues and managed months
        new_customer_revenues = [BASELINE_FEE] * int(new_customers)
        new_customer_managed_months = [0] * int(new_customers)

        customer_revenues = customer_revenues[:customers - int(new_customers)] + new_customer_revenues
        customer_managed_months = customer_managed_months[:customers - int(new_customers)] + new_customer_managed_months

        accounts_managed = int(min(customers, account_managers * CUSTOMERS_PER_ACCOUNT_MANAGER))
        for i in range(accounts_managed):
            if customer_managed_months[i] < 6:
                customer_managed_months[i] += 1
            customer_revenues[i] = BASELINE_FEE * ((1 + REVENUE_INCREASE_RATE) ** customer_managed_months[i])

        # Reset managed months for unmanaged accounts
        for i in range(accounts_managed, customers):
            customer_managed_months[i] = 0
            customer_revenues[i] = BASELINE_FEE

        # Calculate monthly revenue
        monthly_revenue = sum(customer_revenues)
        monthly_revenue_arr.append(monthly_revenue)
        cumulative_revenue += monthly_revenue

    return cumulative_revenue

# Sensitivity Analysis Function
def sensitivity_analysis(base_allocations):
    baseline_revenue = calculate_cumulative_revenue(base_allocations, len(base_allocations))

    constants = {
        "BASELINE_FEE": BASELINE_FEE,
        "ORGANIC_CUSTOMERS": ORGANIC_CUSTOMERS,
        "BASE_CHURN_RATE": BASE_CHURN_RATE,
        "INITIAL_CSAT": INITIAL_CSAT,
        "CSAT_IMPROVEMENT": CSAT_IMPROVEMENT,
        "NEW_CUSTOMERS_PER_SALESPERSON": NEW_CUSTOMERS_PER_SALESPERSON,
        "CUSTOMERS_PER_ACCOUNT_MANAGER": CUSTOMERS_PER_ACCOUNT_MANAGER,
        "REVENUE_INCREASE_RATE": REVENUE_INCREASE_RATE,
        "CSAT_CHURN_REDUCTION": CSAT_CHURN_REDUCTION
    }

    impacts = []
    perturbation_factor = 0.1

    for constant, original_value in constants.items():
        # Increase the constant by 1%
        increased_value = original_value * (1 + perturbation_factor)
        globals()[constant] = increased_value
        increased_revenue = calculate_cumulative_revenue(base_allocations, len(base_allocations))
        increased_percentage_change = ((increased_revenue - baseline_revenue) / baseline_revenue) * 100

        impacts.append({
            "Constant": constant,
            "Original Value": original_value,
            "Perturbation": "Increase",
            "Perturbed Value": increased_value,
            "Revenue Change": increased_revenue,
            "Percentage Change": increased_percentage_change
        })

        # Decrease the constant by 1%
        decreased_value = original_value * (1 - perturbation_factor)
        globals()[constant] = decreased_value
        decreased_revenue = calculate_cumulative_revenue(base_allocations, len(base_allocations))
        decreased_percentage_change = ((decreased_revenue - baseline_revenue) / baseline_revenue) * 100

        impacts.append({
            "Constant": constant,
            "Original Value": original_value,
            "Perturbation": "Decrease",
            "Perturbed Value": decreased_value,
            "Revenue Change": decreased_revenue,
            "Percentage Change": decreased_percentage_change
        })

        globals()[constant] = original_value

    impacts_df = pd.DataFrame(impacts)
    
    # Print the table
    print(impacts_df)

    # Determine the constant with the highest impact
    impacts_df["Impact"] = impacts_df["Revenue Change"].apply(lambda x: abs(x - baseline_revenue))
    most_impactful_constant = impacts_df.groupby("Constant")["Impact"].mean().idxmax()

    return most_impactful_constant, impacts_df

# Example monthly allocations for 12 months
monthly_allocations = [[12, 0, 8], [13, 0, 7], [13, 0, 7], [12, 0, 8], [12, 0, 8], [12, 0, 8], [11, 0, 9], [11, 0, 9], [12, 0, 8], [10, 0, 10], [11, 0, 9], [11, 0, 9], [9, 1, 10], [7, 3, 10], [0, 8, 12], [0, 11, 9], [0, 11, 9], [0, 11, 9], [0, 11, 9], [0, 11, 9], [0, 11, 9], [0, 11, 9], [0, 12, 8], [0, 13, 7]]
most_impactful_constant, impacts_df = sensitivity_analysis(monthly_allocations)

print("Most impactful constant:", most_impactful_constant)

# Plot graphs for each variable
fig = px.bar(impacts_df, x="Constant", y="Percentage Change", color="Perturbation",
             title="Sensitivity Analysis of Revenue Impact",
             labels={"Percentage Change": "Percentage Change in Revenue"})

fig.show()
fig.write_html("graphs/htmls/sensitivity_analysis.html")
