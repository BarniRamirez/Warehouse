import pandas as pd
import time
import json
import math
import ast


slots = pd.read_excel(r"Database\Components.xlsx", sheet_name='Slots')
containers = pd.read_excel(r"Database\Components.xlsx", sheet_name='Containers')
containers['Items'] = containers['Items'].apply(ast.literal_eval)

items = pd.read_excel(r"Database\Items.xlsx", sheet_name='Items')
relations = pd.read_excel(r"Database\Items.xlsx", sheet_name='Relations')

arrivals = pd.read_excel(r"Database\Orders.xlsx", sheet_name='Arrivals')
arrivals['Items'] = arrivals['Items'].apply(ast.literal_eval)
departures = pd.read_excel(r"Database\Orders.xlsx", sheet_name='Departures')
departures['Items'] = departures['Items'].apply(ast.literal_eval)

enumerations = pd.read_excel(r"Database\Components.xlsx", sheet_name='Enumerations', index_col='Enumeration')

to_load = []
to_unload = []
with open(r"Database/dispatching_temp.json", "r") as f:
    dispatching_lots = json.load(f)

print(items.to_string())
print(relations.to_string())
print(slots.to_string())
print(containers.to_string())
print(arrivals.to_string())
print(departures.to_string())
print(enumerations.to_string())
print(dispatching_lots)
# print(f"\n\n {type(arrivals['Items'].iloc[0])}")
#
# exit(666)


def main():
    try:
        while True:
            dispatch_arrivals()
            update_states()
            # print(slots.to_string())
            print(dispatching_lots)
            time.sleep(3)

    except KeyboardInterrupt:
        with pd.ExcelWriter(r"Database/Components.xlsx", mode='a', if_sheet_exists='replace') as writer:
            slots.to_excel(writer, sheet_name='Slots', index=False)
            containers.to_excel(writer, sheet_name='Containers', index=False)
        with pd.ExcelWriter(r"Database/Orders.xlsx", mode='a', if_sheet_exists='replace') as writer:
            arrivals.to_excel(writer, sheet_name='Arrivals', index=False)
            departures.to_excel(writer, sheet_name='Departures', index=False)
        with open("Database/dispatching_temp.json", "w") as temp:
            json.dump(dispatching_lots, temp)
        exit(0)


def update_states():
    # Update Arrivals State
    mask = (arrivals['State'] == 'Scheduled') & (arrivals['Arrival Time'] < pd.Timestamp.now())
    arrivals.loc[mask, 'State'] = 'Arrived'

    mask = (arrivals['State'] == 'Arrived') & (arrivals['Dispatch Time'] < pd.Timestamp.now())
    arrivals.loc[mask, 'State'] = 'Dispatching'

    # Update Slots State
    mask = ((slots['State'] == 'Free') | (slots['State'] == 'Booked')) & (
        slots['ID'].isin(containers.loc[containers['State'] == 'Loading', 'Slot']))
    slots.loc[mask, 'State'] = 'Loading'

    mask = (slots['State'] == 'Occupied') & (
        slots['ID'].isin(containers.loc[containers['State'] == 'Unloading', 'Slot']))
    slots.loc[mask, 'State'] = 'Unloading'

    mask = (slots['State'] == 'Loading') & (slots['ID'].isin(containers.loc[containers['State'] == 'Stored', 'Slot']))
    slots.loc[mask, 'State'] = 'Occupied'

    # empty_containers = (containers['State'] == 'Loading') & (len(containers['Items']) == 0)
    # print(f"\nEmpty Containers: \n{empty_containers}\n")
    # mask = (slots['State'] == 'Loading') & (slots['ID'].isin(containers.loc[empty_containers, 'Slot']))
    # slots.loc[mask, 'State'] = 'Free'
    # containers.loc[empty_containers, 'State'] = 'Free'
    # containers.loc[empty_containers, 'Slot'] = 0


def add_lot(lot, container):
    item = items.loc[items['Name'] == lot['Name']].iloc[0]
    if container['Item Types']:
        found = False
        for si, stored_item in enumerate(container['Items']):
            if lot['Name'] == stored_item['Name']:
                container['Items'][si]['Quantity'] = stored_item['Quantity'] + lot['Quantity']
                found = True
                break
        if not found:
            container['Items'].append(lot)
    else:
        container['Items'].append(lot)

    container['Item Types'] = len(container['Items'])
    container['Filled'] = container['Filled'] + item['Volume'] * lot['Quantity']
    container['Filling'] = math.ceil(container['Filled'] / container['Volume'] * 100)

    print(f"\nFilled: {container['Filled']}\nPercentage: {container['Filling']}")
    return container


def dispatch_arrivals():
    # Prepare dispatching
    mask = arrivals['State'] == 'Dispatching'
    for value in arrivals.loc[mask, 'Items'].values:
        dispatching_lots.extend(list(value))
        # dispatching_lots.extend(json.loads(value.replace("'", '"')))
    arrivals.loc[mask, 'State'] = 'Dispatched'

    # Get item
    disp_lot = dispatching_lots[0]
    item = items.loc[items['Name'] == disp_lot['Name']].iloc[0]
    print(f"\n\nReference Item: {disp_lot}")

    # Get first free fitting container
    mask = (containers['Length'] >= item['Length']) & (containers['Width'] >= item['Width']) & (
                containers['Height'] >= item['Height']) & (containers['State'] == 'Free')
    if mask.any():
        container = containers.loc[mask].iloc[0]
        container_index = containers.loc[mask].index[0]
        print(f"\nSelected container: {container['ID']}\n\n{container.to_string()}\n\n")
    else:
        print("\n\n\n#############   Warehouse Full   #############")
        return

    # Filler FIFO based on volume
    i = -1
    while True:
        i += 1
        disp_lot = dispatching_lots[i]
        print(f"\nDispatching #{i} Item: {disp_lot}")

        if disp_lot['Quantity'] == 0:
            print(f"\nInvalid item quantity.\n")
            dispatching_lots.pop(i)
            continue

        if not ((container['Length'] >= item['Length']) & (container['Width'] >= item['Width']) & (
                container['Height'] >= item['Height'])):
            print(f"\nNot right dimensions.\n")
            continue

        item = items.loc[items['Name'] == disp_lot['Name']].iloc[0]
        print(f"\n{item.to_string()}\n")

        capacity = math.floor((container['Volume'] - container['Filled']) / item['Volume'])
        print(f"\nI can insert {capacity} items")

        if capacity == 0:
            print("\nItem too big, Container is full\n")
            break

        if capacity >= disp_lot['Quantity']:
            container = add_lot(disp_lot, container)
            dispatching_lots.pop(i)
        else:
            partial_lot = {
                'Name': disp_lot['Name'],
                'Quantity': capacity,
            }
            container = add_lot(partial_lot, container)
            dispatching_lots[i]['Quantity'] = dispatching_lots[i]['Quantity'] - partial_lot['Quantity']
            break

    container['State'] = 'Loading'
    containers.loc[container_index] = container
    print(f"\nFilled Container:\n\n{containers.loc[container_index].to_string()}\n\n")


if __name__ == "__main__":
    main()
