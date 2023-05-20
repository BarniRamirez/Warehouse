import pandas as pd


ordered_items = ['USB Flash Drive', 'Wireless Mouse', 'AAA Batteries', 'Food Storage Containers',
                 'Toolbox', 'Screw Assortment Kit', 'Utility Knife', 'Measuring Tape',
                 'Wall Clock', 'Aromatherapy Diffuser', 'Bath Towels', 'Lipstick', 'Soccer Ball']
id_start = 50501
append_arrivals = False


items = pd.read_excel(r"Database\Items.xlsx", sheet_name='Items')
ordered_items = list(set(ordered_items))

if append_arrivals:
    arrivals_df = pd.read_excel(r"Database\Arrivals.xlsx", sheet_name='Arrivals')
else:
    arrivals_df = pd.DataFrame()

arrivals = []
for ordered_item in ordered_items:
    supplier = items.loc[items['Name'] == ordered_item, 'Supplier'].values[0]
    quantity = items.loc[items['Name'] == ordered_item, 'Min Order Quantity'].values[0]
    found = False
    for s, search in enumerate(arrivals):
        if search['Supplier'] == supplier:
            arrivals[s]['Items'].append((ordered_item, quantity))
            found = True
            break
    if not found:
        arrivals.append({
            "ID": id_start + len(arrivals) + len(arrivals_df) + 1,
            "Arrival Time": pd.Timestamp.now(),
            "Dispatch Time": pd.Timestamp.now(),
            "Supplier": supplier,
            "Items": [(ordered_item, quantity)]
        })


arrivals_df = pd.concat([arrivals_df, pd.DataFrame(arrivals)], ignore_index=True)

with pd.ExcelWriter(r"Database/Arrivals.xlsx", mode='a', if_sheet_exists='replace') as writer:
    arrivals_df.to_excel(writer, sheet_name='Arrivals', index=False)

print(arrivals_df.to_string())
