import pandas as pd
import time
import json


slots = pd.read_excel(r"Database\Components.xlsx", sheet_name='Slots')
containers = pd.read_excel(r"Database\Components.xlsx", sheet_name='Containers')
enumerations = pd.read_excel(r"Database\Components.xlsx", sheet_name='Enumerations', index_col='Enumeration')
items = pd.read_excel(r"Database\Items.xlsx", sheet_name='Items')
relations = pd.read_excel(r"Database\Items.xlsx", sheet_name='Relations')
arrivals = pd.read_excel(r"Database\Arrivals.xlsx", sheet_name='Arrivals')
departures = pd.read_excel(r"Database\Orders.xlsx", sheet_name='Departures')

to_load = []
to_unload = []
with open(r"Database/dispatching_temp.json", "r") as f:
    dispatching_items = json.load(f)

print(items.to_string())
print(relations.to_string())
print(slots.to_string())
print(containers.to_string())
print(arrivals.to_string())
print(departures.to_string())
print(enumerations.to_string())
print(dispatching_items)


def main():
    try:
        while True:
            dispatch_arrivals()
            update_states()
            # print(slots.to_string())
            print(dispatching_items)
            time.sleep(3)

    except KeyboardInterrupt:
        with pd.ExcelWriter(r"Database/Components.xlsx", mode='a', if_sheet_exists='replace') as writer:
            slots.to_excel(writer, sheet_name='Slots', index=False)
            containers.to_excel(writer, sheet_name='Containers', index=False)
        with pd.ExcelWriter(r"Database/Orders.xlsx", mode='a', if_sheet_exists='replace') as writer:
            arrivals.to_excel(writer, sheet_name='Arrivals', index=False)
            departures.to_excel(writer, sheet_name='Departures', index=False)
        with open("Database/dispatching_temp.json", "w") as temp:
            json.dump(dispatching_items, temp)
        exit(0)


def update_states():
    # Update Arrivals State
    mask = (arrivals['State'] == 'Scheduled') & (arrivals['Arrival Time'] < pd.Timestamp.now())
    arrivals.loc[mask, 'State'] = 'Arrived'

    mask = (arrivals['State'] == 'Arrived') & (arrivals['Dispatch Time'] < pd.Timestamp.now())
    arrivals.loc[mask, 'State'] = 'Dispatching'

    # Update Slots State
    mask = ((slots['State'] == 'Free') | (slots['State'] == 'Picking')) & (
        slots['ID'].isin(containers.loc[containers['State'] == 'Loading', 'Slot']))
    slots.loc[mask, 'State'] = 'Loading'

    mask = (slots['State'] == 'Occupied') & (
        slots['ID'].isin(containers.loc[containers['State'] == 'Unloading', 'Slot']))
    slots.loc[mask, 'State'] = 'Unloading'

    mask = (slots['State'] == 'Loading') & (slots['ID'].isin(containers.loc[containers['State'] == 'Stored', 'Slot']))
    slots.loc[mask, 'State'] = 'Occupied'

    empty_containers = (containers['State'] == 'Loading') & len(containers['Items']) == 0
    mask = (slots['State'] == 'Loading') & (slots['ID'].isin(containers.loc[empty_containers, 'Slot']))
    slots.loc[mask, 'State'] = 'Free'
    containers.loc[empty_containers, 'State'] = 'Free'
    containers.loc[empty_containers, 'Slot'] = 0


def dispatch_arrivals():
    mask = arrivals['State'] == 'Dispatching'
    for value in arrivals.loc[mask, 'Items'].values:
        dispatching_items.extend(json.loads(value.replace("'", '"')))
    arrivals.loc[mask, 'State'] = 'Dispatched'

    mask = items['Name'] == dispatching_items[0]['Name']
    dimensions = list(items.loc[mask, 'Length':'Volume'].values[0])
    print(dimensions[0])
    # print(pd.DataFrame(dispatching_items))


if __name__ == "__main__":
    main()
