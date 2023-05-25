"""
Some useful code to manage database
Save a backup of database before lunching code
"""
import pandas as pd
import random
import json
import ast


# Global Variables

slots = pd.read_excel(r"Database\Components.xlsx", sheet_name='Slots')
slots['Items'] = slots['Items'].apply(ast.literal_eval)
containers = pd.read_excel(r"Database\Components.xlsx", sheet_name='Containers')
containers['Items'] = containers['Items'].apply(ast.literal_eval)

items = pd.read_excel(r"Database\Items.xlsx", sheet_name='Items')
relations = pd.read_excel(r"Database\Items.xlsx", sheet_name='Relations')

arrivals = pd.read_excel(r"Database\Orders.xlsx", sheet_name='Arrivals')
arrivals['Items'] = arrivals['Items'].apply(ast.literal_eval)
arrivals['Arrival Time'] = pd.to_datetime(arrivals['Arrival Time'])
arrivals['Dispatch Time'] = pd.to_datetime(arrivals['Dispatch Time'])

departures = pd.read_excel(r"Database\Orders.xlsx", sheet_name='Departures')
departures['Items'] = departures['Items'].apply(ast.literal_eval)
departures['Placed Time'] = pd.to_datetime(departures['Placed Time'])
departures['Deadline'] = pd.to_datetime(departures['Deadline'])

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
# items['Safety Stock'] = items['Safety Stock'].apply(lambda x: round(x, 0))
# items['Reorder Point'] = items['Safety Stock'] * 2.5
# items['Lot Quantity'] = items['Demand Average'] * random.uniform(0.7, 1.3)
# items['Lot Quantity'] = items['Lot Quantity'].apply(lambda x: round(x, -2))
# items['Stored Quantity'] = items['Demand Average'] * random.uniform(0.3, 1.3)
# items['Stored Quantity'] = items['Stored Quantity'].apply(lambda x: round(x, 0))

# # Compute Volume cm3
# items['cm3'] = (items['Length'] * items['Width'] * items['Height'])/1000

# Write Item
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


# Old Filler

#     Get first dispatching lot
#     disp_lot = dispatching_lots[0]
#     item = items.loc[items['Name'] == disp_lot['Name']].iloc[0]
#     print(f"\n\nReference Item: {disp_lot}")
#
#     # Get first free fitting container
#     mask = (containers['Length'] >= item['Length']) & (containers['Width'] >= item['Width']) & (
#                 containers['Height'] >= item['Height']) & (containers['State'] == 'Free')
#     if mask.any():
#         container = containers.loc[mask].iloc[0]
#         container_index = containers.loc[mask].index[0]
#         print(f"\nSelected container: {container['ID']}\n\n{container.to_string()}\n\n")
#     else:
#         print("\n\n\n#############   Warehouse Full   #############")
#         return
#
#     # Filler FIFO based on volume
#     i = -1
#     while True:
#         i += 1
#         disp_lot = dispatching_lots[i]
#         print(f"\nDispatching #{i} Item: {disp_lot}")
#
#         if disp_lot['Quantity'] == 0:
#             print(f"\nInvalid item quantity.\n")
#             dispatching_lots.pop(i)
#             continue
#
#         if not ((container['Length'] >= item['Length']) & (container['Width'] >= item['Width']) & (
#                 container['Height'] >= item['Height'])):
#             print(f"\nNot right dimensions.\n")
#             continue
#
#         item = items.loc[items['Name'] == disp_lot['Name']].iloc[0]
#         print(f"\n{item.to_string()}\n")
#
#         capacity = math.floor((container['Volume'] - container['Filled']) / item['Volume'])
#         print(f"\nI can insert {capacity} items")
#
#         if capacity == 0:
#             print("\nItem too big, Container is full\n")
#             break
#
#         if capacity >= disp_lot['Quantity']:
#             container = add_lot(disp_lot, container)
#             dispatching_lots.pop(i)
#         else:
#             partial_lot = {
#                 'Name': disp_lot['Name'],
#                 'Quantity': capacity,
#             }
#             container = add_lot(partial_lot, container)
#             dispatching_lots[i]['Quantity'] = dispatching_lots[i]['Quantity'] - partial_lot['Quantity']
#             break
#
#     container['State'] = 'Loading'
#
#     # Assign Slot
#     min_weight = slots.loc[slots['Type'] == container['Type'], 'Path Weight'].min()
#     mask = (slots['Type'] == container['Type']) & (slots['Parth Weight'] == min_weight)
#     container['Slot'] = slots.loc[mask, 'ID'].values[0]
#
#     containers.loc[container_index] = container
#     print(f"\nFilled Container:\n\n{containers.loc[container_index].to_string()}\n\n")

# Reinitialize database
for s, slot in slots.iterrows():
    slots.loc[s, 'State'] = 'Free'
    slots.loc[s, 'Container'] = 0
    slots.loc[s, 'Items'].clear()

for c, cont in containers.iterrows():
    containers.loc[c, 'State'] = 'Free'
    containers.loc[c, 'Slot'] = 0
    containers.loc[c, 'Priority'] = 0
    containers.loc[c, 'Item Types'] = 0
    containers.loc[c, 'Filled'] = 0
    containers.loc[c, 'Filling'] = 0
    containers.loc[c, 'Items'].clear()

dispatching_lots = []

with pd.ExcelWriter(r"Database/Components.xlsx", mode='a', if_sheet_exists='replace') as writer:
    slots.to_excel(writer, sheet_name='Slots', index=False)
    containers.to_excel(writer, sheet_name='Containers', index=False)
with open("Database/dispatching_temp.json", "w") as temp:
    json.dump(dispatching_lots, temp)

