import numpy as np
import pandas as pd
from mip import Model, xsum, maximize, BINARY


def optimize_group(elements: list, items: pd.DataFrame, relations: pd.DataFrame):
    """
    Function that implements the optimization algorithm for creating product groups.
    """

    # Acquisition of the quantity of products in stock
    demands = []
    stored_quantities = []
    for i in range(len(elements)):
        demands.append(items.loc[items['Name'] == elements[i]['Name'], 'Demand Average'].values[0])
        stored_quantities.append(items.loc[items['Name'] == elements[i]['Name'], 'Stored Quantity'].values[0])

    # Definition of the correlation matrix between the elements
    correlation_matrix = np.zeros((len(elements), len(elements)))

    for i in range(len(elements)):
        for j in range(len(elements)):
            if i != j:
                correlation_matrix[i][j] = relations.loc[relations['Product'] == elements[i]['Name'], elements[j]['Name']].values[0]
    # Ensure that the correlation matrix is symmetric and has a main diagonal equal to 0

    # print(correlation_matrix)

    # Model definition
    print("\nStarting the Model...")
    model = Model()
    model.verbose = False  # Set to True to see the model being built

    # Decision variable: Create a binary variable for each element and matrix for correlation
    x = [model.add_var(var_type=BINARY) for _ in elements]
    y = [[model.add_var(var_type=BINARY) for _ in elements] for _ in elements]

    # Objective function: Maximize the correlation between the elements of the group
    print("Defining the Objective Function...")
    model.objective = maximize(xsum(
        correlation_matrix[i][j]
        * demands[i] / stored_quantities[i]
        * y[i][j] for i in range(len(elements)) for j in range(len(elements))
    ))

    # Constraints: The group must contain exactly 4 elements, the matrix y must be consistent with the selected array of elements
    print("Setting the Model Constraints...")
    model += sum(x) == 4

    for i in range(len(elements)):
        for j in range(len(elements)):
            model += y[i][j] <= x[i]              # if x[i] is not present -> y[i][j] = 0
            model += y[i][j] <= x[j]              # if x[j] is not present -> y[i][j] = 0
            model += y[i][j] >= x[i] + x[j] - 1   # if x[i] & x[j] are present -> y[i][j] = 1

    # Optimization
    print("Starting Optimization...\n")
    model.optimize()
    print("\nEnd of Optimization.\n")

    optimal_array = [x[i].x for i in range(len(elements))]
    optimal_group = [elements[i]['Name'] for i in range(len(elements)) if x[i].x == 1.0]
    optimal_matrix = [[y[i][j].x for j in range(len(elements))] for i in range(len(elements))]

    print(f"\n{optimal_array = }")
    print(f"{optimal_group = }")

    # for i in range(len(elements)):
    #     for j in range(len(elements)):
    #         print(optimal_matrix[i][j], end=', ')
    #     print(' ')

    print(f"{model.objective_value = }")

    return optimal_group




