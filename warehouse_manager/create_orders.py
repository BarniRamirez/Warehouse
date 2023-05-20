import pandas as pd
import random
import math


def non_linear_extraction(min_value, max_value, samples_amount, factor, exponent):
    values = list(range(min_value, max_value + 1))
    print(values)

    weights = []
    previous_weights_sum = 0
    for value in values:
        previous_weights_sum = math.ceil(
            previous_weights_sum * factor + value ** exponent)  # Non-linear weights formula
        weights.append(previous_weights_sum)
    weights.reverse()
    print(weights)

    samples = random.choices(values, weights=weights, k=samples_amount)
    return samples


orders_amount = 50
id_start = 600001
append_orders = True
deadline_start = 24
deadline_stop = 48


with open(r"Database\Addresses.txt", "r", encoding='utf-8') as f:
    data = f.read()
addresses = data.split('\n')

items = pd.read_excel(r"Database\Items.xlsx", sheet_name='Items')
relations = pd.read_excel(r"Database\Items.xlsx", sheet_name='Relations')

relations_times_demand = relations
for c in range(1, len(relations)+1):
    relations_times_demand.iloc[:, c] = relations.iloc[:, c] * items.loc[:, 'Demand Average']
print(relations_times_demand.to_string())

if append_orders:
    orders_df = pd.read_excel(r"Database\Orders.xlsx", sheet_name='Orders')
else:
    orders_df = pd.DataFrame()


# Generate orders
orders = []
orders_quantities = non_linear_extraction(1, 10, orders_amount, 1.5, 3)
for n, order_quantity in enumerate(orders_quantities):
    order_items = []
    for q in range(0, order_quantity):
        if len(order_items):
            items_weight = pd.Series([0]*len(items))  # items.loc[:, 'Demand Average']/10
            for i in range(0, len(order_items)):
                items_weight = items_weight + relations_times_demand.loc[:, order_items[i][0]] * order_items[i][1]
        else:
            items_weight = items.loc[:, 'Demand Average']

        items_weight = items_weight.rename('Weight')
        print(pd.DataFrame([items.loc[:, 'Name'], items_weight]).to_string())

        item = random.choices(items.loc[:, 'Name'], weights=items_weight)[0]
        print(item)

        # Create Tuples
        found = False
        for s, search in enumerate(order_items):
            if search[0] == item:
                order_items[s] = (search[0], search[1] + 1)
                found = True
                break
        if not found:
            order_items.append((item, 1))

    # Create Order
    order = {
        "ID": id_start + len(orders_df) + n,
        "Placed Time": pd.Timestamp.now(),
        "Deadline": pd.Timestamp.now() + pd.DateOffset(hours=random.randint(deadline_start, deadline_stop)),
        "Items": order_items,
        "Address": random.choices(addresses)[0]
    }
    orders.append(order)
    print(f'{order_items}\n\n')


orders_df = pd.concat([orders_df, pd.DataFrame(orders)]).sort_values('Deadline', ignore_index=True)

with pd.ExcelWriter(r"Database/Orders.xlsx", mode='a', if_sheet_exists='replace') as writer:
    orders_df.to_excel(writer, sheet_name='Orders', index=False)

print(orders_df.to_string())
