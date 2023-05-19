import pandas as pd
import random
import math

with open(r"Database\Addresses.txt", "r", encoding='utf-8') as f:
    data = f.read()
addresses = data.split('\n')

items = pd.read_excel(r"Database\Items.xlsx", sheet_name='Items')
relations = pd.read_excel(r"Database\Items.xlsx", sheet_name='Relations')

relations_times_demand = relations
for c in range(1, len(relations)+1):
    relations_times_demand.iloc[:, c] = relations.iloc[:, c] * items.loc[:, 'Demand Average']
print(relations_times_demand.to_string())


# Create weights for extracting the number of items for each order
min_items_x_order = 1
max_items_x_order = 10
orders_count = 50  # How many orders?

order_quantity_values = list(range(1, max_items_x_order + 1))
print(order_quantity_values)

order_quantity_weights = []
previous_weights_sum = 0
for value in order_quantity_values:
    previous_weights_sum = math.ceil(previous_weights_sum * 1.5 + value ** 3)  # Non-linear order_quantity_weights formula
    order_quantity_weights.append(previous_weights_sum)
order_quantity_weights.reverse()
print(order_quantity_weights)


# Generate orders
orders = []
for n in range(0, orders_count):
    order_quantity = random.choices(order_quantity_values, weights=order_quantity_weights)[0]
    order_items = []
    for q in range(0, order_quantity):
        if len(order_items):
            items_weight = pd.Series([0]*len(items))  # items.loc[:, 'Demand Average']/10
            for i in range(0, len(order_items)):
                items_weight = items_weight + relations_times_demand.loc[:, order_items[i]]
        else:
            items_weight = items.loc[:, 'Demand Average']

        items_weight = items_weight.rename('Weight')
        print(pd.DataFrame([items.loc[:, 'Name'], items_weight]).to_string())

        item = random.choices(items.loc[:, 'Name'], weights=items_weight)[0]
        order_items.append(item)
        print(item)

    orders.append(order_items)
    print(f'{order_items}\n\n')


# Makes order tuples
orders_tuple = []
for order in orders:
    order_tuple = []  # (item, quantity)
    for i, item in enumerate(order):
        if i == 0:
            order_tuple.append((item, 1))
        else:
            found = False
            for s, search in enumerate(order_tuple):
                if search[0] == item:
                    order_tuple[s] = (search[0], search[1] + 1)
                    found = True
                    break
            if not found:
                order_tuple.append((item, 1))

    orders_tuple.append(order_tuple)
    print(order_tuple)


# Generate others order fields
start_from_id = 600001
deadline_start = 24
deadline_stop = 48
complete_orders = []
for n, ot in enumerate(orders_tuple):
    order = {
        "ID": start_from_id + n,
        "Placed Time": pd.Timestamp.now(),
        "Deadline": pd.Timestamp.now() + pd.DateOffset(hours=random.randint(deadline_start, deadline_stop)),
        "Items": ot,
        "Address": random.choices(addresses)[0]
    }
    complete_orders.append(order)
orders_df = pd.DataFrame(complete_orders)
# orders_df['Address'] = orders_df['Address'].str.decode('utf-8')

with pd.ExcelWriter(r"Database/Orders.xlsx", mode='a', if_sheet_exists='replace') as writer:
    orders_df.to_excel(writer, sheet_name='Orders', index=False)
