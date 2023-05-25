import pandas as pd
import time
import json
import math
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


def save_to_database():
    with pd.ExcelWriter(r"Database/Components.xlsx", mode='a', if_sheet_exists='replace') as writer:
        slots.to_excel(writer, sheet_name='Slots', index=False)
        containers.to_excel(writer, sheet_name='Containers', index=False)
    with pd.ExcelWriter(r"Database/Items.xlsx", mode='a', if_sheet_exists='replace') as writer:
        items.to_excel(writer, sheet_name='Items', index=False)
    with pd.ExcelWriter(r"Database/Orders.xlsx", mode='a', if_sheet_exists='replace') as writer:
        arrivals.to_excel(writer, sheet_name='Arrivals', index=False)
        departures.to_excel(writer, sheet_name='Departures', index=False)
    with open("Database/dispatching_temp.json", "w") as temp:
        json.dump(dispatching_lots, temp)


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


def add_one_item(item: pd.Series, container: pd.Series):
    """ Add one item to container.
    :param item: item
    :param container: container
    :return: filled container
    """
    if not (item['Name'] in [dispatching_lot['Name'] for dispatching_lot in dispatching_lots]):
        return container
    if container['Item Types']:
        found = False
        for si, stored_item in enumerate(container['Items']):
            if item['Name'] == stored_item['Name']:
                container['Items'][si]['Quantity'] = stored_item['Quantity'] + 1
                found = True
                break
        if not found:
            container['Items'].append({"Name": item['Name'], "Quantity": 1})
    else:
        container['Items'].append({"Name": item['Name'], "Quantity": 1})

    container['Item Types'] = len(container['Items'])
    container['Filled'] = container['Filled'] + item['Volume']
    container['Filling'] = math.ceil(container['Filled'] / container['Volume'] * 100)

    lot_index = [dispatching_lot['Name'] for dispatching_lot in dispatching_lots].index(item['Name'])
    dispatching_lots[lot_index]['Quantity'] -= 1
    if dispatching_lots[lot_index]['Quantity'] == 0:
        dispatching_lots.pop(lot_index)

    return container


def fill_with_many_items(items_names: list, container: pd.Series):
    """ Fill container with many items.
    :param items_names: list of items names
    :param container: container
    :return: filled container
    """
    filling_percentage = 95
    while True:
        if len(items_names) == 0:
            print("\nContainer Partially Filled\n")
            break

        items_volume = list(items.loc[items['Name'].isin(items_names), 'Volume'])
        remaining_volume = (filling_percentage - container['Filling']) / 100 * container['Volume']
        # print(f"\nRemaining Volume: {remaining_volume}")

        if all(remaining_volume < v for v in items_volume):
            print("\nContainer Filled\n")
            break

        for i, item_name in enumerate(items_names):
            item = items.loc[items['Name'] == item_name].iloc[0]
            remaining_volume = (filling_percentage - container['Filling']) / 100 * container['Volume']
            if remaining_volume <= item['Volume']:
                items_names.pop(i)
                continue
            if item_name not in [dispatching_lot['Name'] for dispatching_lot in dispatching_lots]:
                items_names.pop(i)
                continue

            # print(f"Item: {item['Name']}, Volume: {item['Volume']}, Remaining Volume: {remaining_volume}")
            container = add_one_item(item, container)

    print(f"\nFilled: {container['Filled']}\nPercentage: {container['Filling']}")
    return container


def update_dispatching():
    mask = arrivals['State'] == 'Dispatching'
    for value in arrivals.loc[mask, 'Items'].values:
        dispatching_lots.extend(list(value))
    arrivals.loc[mask, 'State'] = 'Dispatched'


def verify_dimensions(container, selected_lots, quantity):
    container_dimensions = [container['Length'], container['Width'], container['Height']]
    filled_volume = 0

    for lot in selected_lots:
        item = items.loc[items['Name'] == lot['Name']].iloc[0]
        item_dimensions = [item['Length'], item['Width'], item['Height']]
        # print(f"Item: {item['Name']}, Group volume: {item['Volume']*quantity}, Remaining Volume: {container['Volume'] - filled_volume}")

        container_dimensions_temp = container_dimensions
        for i, i_dim in enumerate(item_dimensions):
            for c, c_dim in enumerate(container_dimensions_temp):
                if c_dim > i_dim:
                    container_dimensions_temp.pop(c)
                    break

        filled_volume += item['Volume'] * quantity
        if not (len(container_dimensions_temp) == 0 and container['Volume'] >= filled_volume):
            return False
    return True


def are_similar(container, container_ref: pd.Series) -> bool:
    if len(container['Items']) != 0 and len(container_ref['Items']) != 0:
        container_items_names = [item['Name'] for item in container['Items']]
        container_ref_items_names = [item['Name'] for item in container_ref['Items']]
        if set(container_items_names) == set(container_ref_items_names):
            if container['Slot'] != 0:
                return True
    return False


def book_free_slot(container: pd.Series):
    # Slot indexes of the containers with same items
    mask = containers.apply(lambda x: are_similar(x, container), axis=1)

    if any(mask):
        print(f"\n\nEqual container found.\n\n")
        similar_slots = containers.loc[mask, 'Slot'].values
        print(similar_slots)
        equal_slots_indexes = slots.index[slots['ID'].isin(similar_slots)].values

        # Find suitable slots
        # Not load close to a similar container
        path_distance_from_equal = 6
        while True:
            mask = pd.Series(True, slots.index)
            # print(mask.values)
            for esi in equal_slots_indexes:
                print(f"\nSimilar slot: {slots.loc[esi, 'ID']} "
                      f"Path Weight of similar slot: {slots.loc[esi, 'Path Weight']}")
                filter_max = slots.loc[esi, 'Path Weight'] + path_distance_from_equal
                filter_min = slots.loc[esi, 'Path Weight'] - path_distance_from_equal
                print(f"Avoiding Weights from: {filter_min} to {filter_max}")
                mask = mask & ((slots['Path Weight'] > filter_max) | (slots['Path Weight'] < filter_min))

            mask = mask & (slots['Type'] == container['Type']) & (slots['State'] == 'Free')

            # print(mask.values)
            if any(mask):
                break
            if path_distance_from_equal == 0:
                break
            path_distance_from_equal -= 1
            print(f"\n\nDecreasing path distance from equal to: {path_distance_from_equal}")

    else:
        print(f"\n\nNot equal container found.\n\n")
        mask = (slots['Type'] == container['Type']) & (slots['State'] == 'Free')

    if not any(mask):
        mask = (slots['Type'] == container['Type']) & (slots['State'] == 'Free')

    if any(mask):
        print("Book the suitable slot with the lowest path weight")
        slot_index = slots.loc[mask, 'Path Weight'].idxmin()
        slots.loc[slot_index, 'State'] = 'Booked'
        slots.loc[slot_index, 'Container'] = container['ID']
        slots.loc[slot_index, 'Items'].extend(container['Items'])
        slots.loc[slot_index, 'Items Count'] += len(slots.loc[slot_index, 'Items'])
        print(f"\nBooked slot: {slots.loc[slot_index, 'ID']}. Path Weight: {slots.loc[slot_index, 'Path Weight']}")
        print(f"With container: {slots.loc[slot_index, 'Container']}\n")
        return slot_index

    print("No suitable slot found")
    return None


def dispatch_arrivals():
    # Select four items
    selected_items = dispatching_lots[: min(4, len(dispatching_lots))]
    print(f"\nSelected lots: {selected_items}")
    n = len(selected_items)
    if not n:
        return

    # Select an adeguate container. It must have all dimensions grater than the selected items.
    quantity = 60
    mask = pd.Series(False, containers.index)
    while True:
        if quantity < 4:
            break
        mask = (
                (containers.apply(verify_dimensions, axis=1, args=(selected_items, round(quantity/n, 0)))) &
                (containers['State'] == 'Free')
        )
        if any(mask):
            break
        else:
            quantity = quantity/2

    if not any(mask):
        mask = (containers.apply(verify_dimensions, axis=1, args=(selected_items, 1))) & (containers['State'] == 'Free')
    if not any(mask):
        print(f"No adequate container found. Selected items: {selected_items}")
        return
    container = containers.loc[mask].iloc[0]
    container_index = containers.index[mask].values[0]
    print(f"\nFitting container: \n{container}\n")

    # Fill container with selected items
    selected_items_name = [lot['Name'] for lot in selected_items]
    container = fill_with_many_items(selected_items_name, container)
    container['State'] = 'Loading'
    container['Priority'] = containers.loc[:, 'Priority'].max() + 1
    containers.loc[container_index] = container

    # Book a slot for the container
    print(f"\nBooking a slot for the container: \n{container['ID']}\n")
    slot_index = book_free_slot(container)
    if slot_index is None:
        container['Sate'] = 'Waiting'
        containers.loc[container_index] = container
        print('Not slot index')
        return
    container['Slot'] = slots.loc[slot_index, 'ID']

    # Save changes to database
    containers.loc[container_index] = container

    # Update Stored Quantity
    for item in slots.loc[slot_index, 'Items']:
        item_index = items.loc[items['Name'] == item['Name']].index[0]
        items.loc[item_index, 'Stored Quantity'] += item['Quantity']

    print(f"\nFilled container: \n{ containers.loc[container_index] }\n \nSlot: { slots.loc[slot_index, 'ID'] }\n")


def main():
    try:
        while True:
            update_dispatching()
            dispatch_arrivals()
            update_states()
            # save_to_database()

            print(dispatching_lots)
            # time.sleep(1)

    except KeyboardInterrupt:
        save_to_database()
        print("\nProgram terminated by user.")
        exit(0)
    # except Exception as e:
    #     save_to_database()
    #     print(f"Exception Raised: \n{e}")
    #     exit(1)


if __name__ == "__main__":
    main()
