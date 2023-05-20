"""
Some useful code to manage database
Save a backup of database before lunching code
"""

import pandas as pd
import random


# Import database files
slots = pd.read_excel(r"Database\Components.xlsx", sheet_name='Slots')
containers = pd.read_excel(r"Database\Components.xlsx", sheet_name='Containers')
items = pd.read_excel(r"Database\Items.xlsx", sheet_name='Items')
relations = pd.read_excel(r"Database\Items.xlsx", sheet_name='Relations')

print(items.to_string())
print(relations.to_string())
print(slots.to_string())
print(containers.to_string())


# # Fill relation table from upper triangular table
# for i in range(0, len(relations)):  # Row
#     for j in range(0, len(relations)):
#         if i < j+1:
#             relations.iloc[j, i+1] = relations.iloc[i, j+1]
#
# print(relations.to_string())
#
# with pd.ExcelWriter(r"Database\Items.xlsx", mode='a', if_sheet_exists='replace') as writer:
#     relations.to_excel(writer, sheet_name='Relations', index=False)


# # Compute Safety Stock, Reorder Point, Min Order Quantity
# items['Safety Stock'] = items['Demand Average'] / 30 * items['Lead Time'] * 1.2
# items['Reorder Point'] = items['Safety Stock'] * 2.5
# items['Min Order Quantity'] = items['Demand Average'] * random.uniform(2, 3)
# items['Min Order Quantity'] = items['Min Order Quantity'].apply(lambda x: round(x, -2))
#
# print(items.to_string())
#
# with pd.ExcelWriter(r"Database\Items.xlsx", mode='a', if_sheet_exists='replace') as writer:
#     items.to_excel(writer, sheet_name='Items', index=False)
