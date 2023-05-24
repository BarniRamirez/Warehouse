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
