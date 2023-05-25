# relations_squared = relations
# for c in range(1, len(relations)+1):
#     relations_squared.iloc[:, c] = relations.iloc[:, c] ** 2
# print(relations_squared.to_string())

# print(relations_times_demand.iloc[:, 1:51].max().max())
# relations_times_demand.iloc[:, 1:51] = relations_times_demand.iloc[:, 1:51] / relations_times_demand.iloc[:, 1:51].max().max()
# print(relations_times_demand.to_string())


# orders_quantities = random.choices(order_quantity_values, weights=order_quantity_weights, k=samples_amount)
# orders_quantities.sort()
# print(orders_quantities)
#
# orders_quantities_iter = []
# for i in range(0, samples_amount):
#     orders_quantities_iter.append(random.choices(order_quantity_values, weights=order_quantity_weights)[0])
# orders_quantities_iter.sort()
# print(orders_quantities_iter)

# def fill_with_one_lot(lot, container):
#     item = items.loc[items['Name'] == lot['Name']].iloc[0]
#     if container['Item Types']:
#         found = False
#         for si, stored_item in enumerate(container['Items']):
#             if lot['Name'] == stored_item['Name']:
#                 container['Items'][si]['Quantity'] = stored_item['Quantity'] + lot['Quantity']
#                 found = True
#                 break
#         if not found:
#             container['Items'].append(lot)
#     else:
#         container['Items'].append(lot)
#
#     container['Item Types'] = len(container['Items'])
#     container['Filled'] = container['Filled'] + item['Volume'] * lot['Quantity']
#     container['Filling'] = math.ceil(container['Filled'] / container['Volume'] * 100)
#
#     print(f"\nFilled: {container['Filled']}\nPercentage: {container['Filling']}")
#     return container


# # Check the adjacent slots
# mask = pd.Series([False] * len(slots))
# print(mask)
# for esi in equal_slots_indexes:
#     # Create a boolean mask to select adjacent slots
#
#     if slots.loc[esi, 'TargetX'] > 0:
#         mask_x = (slots['TargetX'].between(slots.loc[esi, 'TargetX'] - 1, slots.loc[esi, 'TargetX'] + 1))
#     else:
#         mask_x = pd.Series([False] * len(slots))
#     if slots.loc[esi, 'TargetZ'] > 0:
#         mask_z = (slots['TargetZ'].between(slots.loc[esi, 'TargetZ'] - 1, slots.loc[esi, 'TargetZ'] + 1))
#     else:
#         mask_z = pd.Series([False] * len(slots))
#
#     mask = (mask | mask_x | mask_z)
#     print(mask)
#     print(type(mask))
# else:
#     print(f"\n\nNot similar container found.\n\n")
#
# # Print how many trues are in the mask
# print(f"\n\n{mask.sum()} trues in the mask.\n\n")
#
# # Select the minimum path weight slot
#
# mask = (slots['Type'] == container['Type']) & (slots['State'] == 'Free')
# slot_index = slots.loc[mask, 'Path Weight'].idxmin()