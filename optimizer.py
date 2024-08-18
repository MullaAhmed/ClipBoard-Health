from revenue import calculate_cumulative_revenue

NUM_MONTHS = 24
TOTAL_EMPLOYEES = 20


import random
from deap import base, creator, tools, algorithms



# Create the genetic algorithm components
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

# Define how to create a single month's allocation
def create_month_allocation():
    allocation = [0, 0, 0]
    remaining = TOTAL_EMPLOYEES
    for i in range(2):
        value = random.randint(0, remaining)
        allocation[i] = value
        remaining -= value
    allocation[2] = remaining
    return allocation

# Define how to create an individual (full allocation for all months)
toolbox.register("month_allocation", create_month_allocation)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.month_allocation, n=NUM_MONTHS)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Define the evaluation function
def evaluate(individual):
    return (calculate_cumulative_revenue(individual,NUM_MONTHS)[0],)

toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

# Set up the genetic algorithm
population = toolbox.population(n=100000)
ngen = 50
cxpb = 0.7
mutpb = 0.2

# Run the genetic algorithm
algorithms.eaSimple(population, toolbox, cxpb=cxpb, mutpb=mutpb, ngen=ngen, verbose=True)

# Get the best individual
best_ind = tools.selBest(population, k=1)[0]
best_revenue = evaluate(best_ind)[0]

print(f"Best allocation: {best_ind}")
print(f"Best cumulative revenue: {best_revenue}")
print(f"\nTotal cumulative revenue over {NUM_MONTHS} months: ${best_revenue:,.2f}")
