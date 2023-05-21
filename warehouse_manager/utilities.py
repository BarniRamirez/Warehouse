"""
Some useful code to manage database
Save a backup of database before lunching code
"""
import pandas as pd
import random
import json
import ast


# Import database files
slots = pd.read_excel(r"Database\Components.xlsx", sheet_name='Slots')
containers = pd.read_excel(r"Database\Components.xlsx", sheet_name='Containers')
items = pd.read_excel(r"Database\Items.xlsx", sheet_name='Items')
relations = pd.read_excel(r"Database\Items.xlsx", sheet_name='Relations')

print(items.to_string())
# print(relations.to_string())
# print(slots.to_string())
# print(containers.to_string())

# # Relations
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

# # Items
# # Compute Safety Stock, Reorder Point, Min Order Quantity
# items['Safety Stock'] = items['Demand Average'] / 30 * items['Lead Time'] * 1.2
# items['Reorder Point'] = items['Safety Stock'] * 2.5
# items['Min Order Quantity'] = items['Demand Average'] * random.uniform(2, 3)
# items['Min Order Quantity'] = items['Min Order Quantity'].apply(lambda x: round(x, -2))

# # Compute Volume cm3
# items['cm3'] = (items['Length'] * items['Width'] * items['Height'])/1000

# # Write Item
# print(items.to_string())
# with pd.ExcelWriter(r"Database\Items.xlsx", mode='a', if_sheet_exists='replace') as writer:
#     items.to_excel(writer, sheet_name='Items', index=False)


# # Convert dimension cell to data
# data = []
# for i, item in items.iterrows():
#     dimensions = ast.literal_eval(item['Dimensions'])
#     print(i)
#     print(dimensions)
#     data.append({
#         "Length": dimensions[0],
#         "Width":  dimensions[1],
#         "Height": dimensions[2]
#     })
#     print(data)
# items_df = pd.concat([items, pd.DataFrame(data)], axis=1)
# print(items_df.to_string())
#
# with pd.ExcelWriter(r"Database\Items.xlsx", mode='a', if_sheet_exists='replace') as writer:
#     items_df.to_excel(writer, sheet_name='Items', index=False)

