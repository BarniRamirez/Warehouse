import pandas as pd
import random


arrivals_amount = 50
id_start = 50001
append_arrivals = True


items = pd.read_excel(r"Database\Items.xlsx", sheet_name='Items')

if append_arrivals:
    arrivals_df = pd.read_excel(r"Database\Arrivals.xlsx", sheet_name='Arrivals')
else:
    arrivals_df = pd.DataFrame()


suppliers = []
suppliers_weights = []
suppliers_items = []
for i in range(0, len(items)):
    found = False
    for s, search in enumerate(suppliers):
        if search == items.loc[i, 'Supplier']:
            suppliers_weights[s] += items.loc[i, 'Demand Average']
            suppliers_items[s].append(items.loc[i, 'Name'])
            found = True
            break
    if not found:
        suppliers.append(items.loc[i, 'Supplier'])
        suppliers_weights.append(items.loc[i, 'Demand Average'])
        suppliers_items.append([items.loc[i, 'Name']])

print(suppliers)
print(suppliers_weights)
print(suppliers_items)


# Create Arrivals
arrivals = []
for a in range(0, arrivals_amount):
    supplier = random.choices(suppliers, weights=suppliers_weights)[0]
    supplied_items = suppliers_items[suppliers.index(supplier)]
    items_weights = []
    for item in supplied_items:
        items_weights.append(items.loc[items['Name'] == item, 'Demand Average'].values[0])
    arrival_items_name = list(set(random.choices(supplied_items, weights=items_weights, k=len(supplied_items))))
    print(supplier)
    print(items_weights)
    print(arrival_items_name)

    # Create Tuples
    arrival_items = []
    for item in arrival_items_name:
        quantity = items.loc[items['Name'] == item, 'Min Order Quantity'].values[0]
        arrival_items.append((item, quantity))

    # Create Arrival
    arrivals.append({
        "ID": id_start + len(arrivals_df) + a,
        "Arrival Time": pd.Timestamp.now(),
        "Dispatch Time": pd.Timestamp.now(),
        "Supplier": supplier,
        "Items": arrival_items
    })

arrivals_df = pd.concat([arrivals_df, pd.DataFrame(arrivals)], ignore_index=True)

with pd.ExcelWriter(r"Database/Arrivals.xlsx", mode='a', if_sheet_exists='replace') as writer:
    arrivals_df.to_excel(writer, sheet_name='Arrivals', index=False)

print(arrivals_df.to_string())
