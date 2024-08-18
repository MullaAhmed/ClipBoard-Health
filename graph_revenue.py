import plotly.graph_objs as go
import plotly.offline as pyo

# Constants
BASELINE_FEE = 100
ORGANIC_CUSTOMERS = 25
BASE_CHURN_RATE = 0.1
BASE_CSAT = 70
CSAT_IMPROVEMENT = 1
NEW_CUSTOMERS_PER_SALESPERSON = 5
CUSTOMERS_PER_ACCOUNT_MANAGER = 25
REVENUE_INCREASE_RATE = 0.2
CSAT_CHURN_REDUCTION = 0.15

# Calculate the churn rate based on CSAT
# def calculate_churn_rate(csat_score):
#     return BASE_CHURN_RATE * (0.85 ** (csat_score - BASE_CSAT))

def calculate_churn_rate(csat_score):
    return BASE_CHURN_RATE * ((1-CSAT_CHURN_REDUCTION) ** (csat_score - 70))


# assumption that churn rate is 10% and CSAT score is 70

# Calculate revenue from account-managed customers
def calculate_account_manager_revenue(managed_customer_count, months_managed):
    month = min(months_managed, 6)
    total_revenue = managed_customer_count * BASELINE_FEE * (1 + REVENUE_INCREASE_RATE) ** month
    return total_revenue

# Calculate cumulative revenue given allocations
def calculate_cumulative_revenue(monthly_allocations):
    number_of_months = len(monthly_allocations)
    initial_customer_base = 1000
    current_csat_score = BASE_CSAT
    cumulative_revenue = 0
    
    current_customer_base = initial_customer_base
    
    for month_index in range(number_of_months):
        new_business_team_members, account_managers, support_agents = monthly_allocations[month_index]
        
        # Calculate new customers acquired
        new_customer_count = ORGANIC_CUSTOMERS + new_business_team_members * NEW_CUSTOMERS_PER_SALESPERSON
        
        # Calculate churn rate and churned customers
        churn_rate = calculate_churn_rate(current_csat_score + support_agents * CSAT_IMPROVEMENT)
        churned_customer_count = int(current_customer_base * churn_rate)
        
        # Calculate the number of customers managed by account managers
        managed_customer_count = int(min(current_customer_base - churned_customer_count, CUSTOMERS_PER_ACCOUNT_MANAGER * account_managers))
       
        # Calculate monthly revenue
        revenue_from_existing_customers = (current_customer_base + new_customer_count - churned_customer_count - managed_customer_count) * BASELINE_FEE
        revenue_from_managed_customers = calculate_account_manager_revenue(managed_customer_count, month_index + 1)
        
        monthly_revenue = revenue_from_existing_customers + revenue_from_managed_customers 
        
        # Update cumulative revenue
        cumulative_revenue += monthly_revenue
        
        # Update customer base and CSAT for the next month
        current_customer_base = current_customer_base - churned_customer_count + new_customer_count
    
    return cumulative_revenue

# Sensitivity Analysis Function

def sensitivity_analysis(base_allocations):
    # Baseline cumulative revenue
    baseline_revenue = calculate_cumulative_revenue(base_allocations)
    
    constants = {
        "BASELINE_FEE": BASELINE_FEE,
        "ORGANIC_CUSTOMERS": ORGANIC_CUSTOMERS,
        "BASE_CHURN_RATE": BASE_CHURN_RATE,
        "BASE_CSAT": BASE_CSAT,
        "CSAT_IMPROVEMENT": CSAT_IMPROVEMENT,
        "NEW_CUSTOMERS_PER_SALESPERSON": NEW_CUSTOMERS_PER_SALESPERSON,
        "CUSTOMERS_PER_ACCOUNT_MANAGER": CUSTOMERS_PER_ACCOUNT_MANAGER,
        "REVENUE_INCREASE_RATE": REVENUE_INCREASE_RATE,
        "CSAT_CHURN_REDUCTION": CSAT_CHURN_REDUCTION
    }
    
    impacts = {}
    
    # Perturb each constant by 1%
    perturbation_factor = 0.1
    
    for constant, original_value in constants.items():
        # Increase the constant by 1%
        increased_value = original_value * (1 + perturbation_factor)
        
        globals()[constant] = increased_value
        increased_revenue = calculate_cumulative_revenue(base_allocations)
        
        increased_percentage_change = ((increased_revenue - baseline_revenue) / baseline_revenue) * 100
        print(f"Constant: {constant}, Original Value: {original_value}, Increased Value: {increased_value}")
        print(f"Original Revenue: {baseline_revenue}, Revenue Change (Increased): {increased_revenue}, Percentage Change: {increased_percentage_change}%")
        print("--------------------------------------------------\n")
        
        # Decrease the constant by 1%
        decreased_value = original_value * (1 - perturbation_factor)
        globals()[constant] = decreased_value
        decreased_revenue = calculate_cumulative_revenue(base_allocations)
        
        decreased_percentage_change = ((decreased_revenue - baseline_revenue) / baseline_revenue) * 100
        print(f"Constant: {constant}, Original Value: {original_value}, Decreased Value: {decreased_value}")
        print(f"Original Revenue: {baseline_revenue}, Revenue Change (Decreased): {decreased_revenue}, Percentage Change: {decreased_percentage_change}%")
        print("--------------------------------------------------\n")
        
        # Reset the constant to its original value
        globals()[constant] = original_value
        
        # Calculate the average impact of increasing or decreasing the constant
        average_impact = (abs(increased_revenue - baseline_revenue) + abs(decreased_revenue - baseline_revenue)) / 2
        impacts[constant] = average_impact
    
    # Determine the constant with the highest impact
    most_impactful_constant = max(impacts, key=impacts.get)
    
    return most_impactful_constant, impacts

# Calculate the monthly revenue given allocations
def calculate_monthly_revenue(monthly_allocations):
    number_of_months = len(monthly_allocations)
    initial_customer_base = 1000
    current_csat_score = BASE_CSAT
    monthly_revenues = []
    
    current_customer_base = initial_customer_base
    
    for month_index in range(number_of_months):
        new_business_team_members, account_managers, support_agents = monthly_allocations[month_index]
        
        # Calculate new customers acquired
        new_customer_count = ORGANIC_CUSTOMERS + new_business_team_members * NEW_CUSTOMERS_PER_SALESPERSON
        
        # Calculate churn rate and churned customers
        churn_rate = calculate_churn_rate(current_csat_score + support_agents * CSAT_IMPROVEMENT)
        churned_customer_count = int(current_customer_base * churn_rate)
        
        # Calculate the number of customers managed by account managers
        managed_customer_count = int(min(current_customer_base - churned_customer_count, CUSTOMERS_PER_ACCOUNT_MANAGER * account_managers))
        
        # Calculate monthly revenue
        revenue_from_existing_customers = (current_customer_base + new_customer_count - churned_customer_count - managed_customer_count) * BASELINE_FEE
        revenue_from_managed_customers = calculate_account_manager_revenue(managed_customer_count, month_index + 1)
        
        monthly_revenue = revenue_from_existing_customers + revenue_from_managed_customers
        
        # Update monthly revenues list
        monthly_revenues.append(monthly_revenue)
        
        # Update customer base and CSAT for the next month
        current_customer_base = current_customer_base - churned_customer_count + new_customer_count
    
    return monthly_revenues

# Plot monthly revenues
def plot_monthly_revenues(base_allocations):
    constants = {
        "BASELINE_FEE": BASELINE_FEE,
        "ORGANIC_CUSTOMERS": ORGANIC_CUSTOMERS,
        "BASE_CHURN_RATE": BASE_CHURN_RATE,
        "BASE_CSAT": BASE_CSAT,
        "CSAT_IMPROVEMENT": CSAT_IMPROVEMENT,
        "NEW_CUSTOMERS_PER_SALESPERSON": NEW_CUSTOMERS_PER_SALESPERSON,
        "CUSTOMERS_PER_ACCOUNT_MANAGER": CUSTOMERS_PER_ACCOUNT_MANAGER,
        "REVENUE_INCREASE_RATE": REVENUE_INCREASE_RATE,
        "CSAT_CHURN_REDUCTION": CSAT_CHURN_REDUCTION
    }
    
    perturbation_factor = 0.1
    
    for constant, original_value in constants.items():
        # Calculate baseline monthly revenues
        baseline_monthly_revenues = calculate_monthly_revenue(base_allocations)
        
        # Increase the constant by 1%
        increased_value = original_value * (1 + perturbation_factor)
        globals()[constant] = increased_value
        increased_monthly_revenues = calculate_monthly_revenue(base_allocations)
        
        # Decrease the constant by 1%
        decreased_value = original_value * (1 - perturbation_factor)
        globals()[constant] = decreased_value
        decreased_monthly_revenues = calculate_monthly_revenue(base_allocations)
        
        # Reset the constant to its original value
        globals()[constant] = original_value
        
        # Create traces for the plot
        trace_baseline = go.Scatter(
            x=list(range(1, len(base_allocations) + 1)),
            y=baseline_monthly_revenues,
            mode='lines',
            name='Baseline'
        )
        trace_increased = go.Scatter(
            x=list(range(1, len(base_allocations) + 1)),
            y=increased_monthly_revenues,
            mode='lines',
            name=f'{constant} Increased by 10%'
        )
        trace_decreased = go.Scatter(
            x=list(range(1, len(base_allocations) + 1)),
            y=decreased_monthly_revenues,
            mode='lines',
            name=f'{constant} Decreased by 10%'
        )
        
        # Create the layout
        layout = go.Layout(
            title=f'Monthly Revenue Changes for {constant}',
            xaxis=dict(title='Month'),
            yaxis=dict(title='Revenue'),
            showlegend=True
        )
        
        # Create the figure and plot it
        fig = go.Figure(data=[trace_baseline, trace_increased, trace_decreased], layout=layout)
        # fig.savefig(f'revenue/{constant}_monthly_revenue.png')
        pyo.plot(fig, filename=f'{constant}_monthly_revenue.html')

# Example monthly allocations for 12 months
monthly_allocations = [[14, 0, 6], [12, 0, 8], [13, 0, 7], [12, 0, 8], [11, 0, 9], [11, 0, 9], [11, 0, 9], [11, 0, 9], [12, 0, 8], [10, 0, 10], [10, 0, 10], [10, 0, 10], [8, 2, 10], [0, 10, 10], [0, 11, 9], [0, 12, 8], [0, 12, 8], [0, 13, 7], [0, 14, 6], [0, 15, 5], [0, 17, 3], [0, 19, 1], [0, 20, 0], [0, 20, 0]]


# Perform sensitivity analysis and plot graphs
most_impactful_constant, impacts = sensitivity_analysis(monthly_allocations)
plot_monthly_revenues(monthly_allocations)

print("Most impactful constant:", most_impactful_constant)
print("Impacts of each constant:", impacts)
