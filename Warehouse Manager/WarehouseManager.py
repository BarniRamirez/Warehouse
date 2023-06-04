import pandas as pd
from pathlib import Path
import json
# import time
import math
import ast

from optimize_group import *

from PLC import Command, CommandHandler

# Global Variables
slots = pd.read_excel(r"Database\Components.xlsx", sheet_name='Slots')
slots['Items'] = slots['Items'].apply(ast.literal_eval)
containers = pd.read_excel(r"Database\Components.xlsx", sheet_name='Containers')
containers['Items'] = containers['Items'].apply(ast.literal_eval)

chs = [
    # CommandHandler('192.168.0.10', "Area1",  # Handles commands for Area1
    #                targets=slots.loc[slots['Area'] == 1].apply(lambda row: (row['TargetX'], row['TargetZ']),
    #                                                            axis=1).tolist()),
    # CommandHandler('localhost', "Area2-3",  # Handles commands for Area2 and Area3
    #                targets=slots.loc[slots['Area'] > 1].apply(lambda row: (row['TargetX'], row['TargetZ']),
    #                                                           axis=1).tolist()),
    CommandHandler('localhost', "all",  # Handles commands for all areas
                   targets=slots.loc[slots['Area'] > 0].apply(lambda row: (row['TargetX'], row['TargetZ']),
                                                              axis=1).tolist())
]
commands_to_send = []
commands_done = []
commands_error = []

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

file_path = Path("Database/Temp/dispatching_temp.json")

if file_path.exists():
    with open(file_path, "r") as f:
        dispatching_lots = json.load(f)
else:
    dispatching_lots = []

print(items.to_string())
print(relations.to_string())
print(slots.to_string())
print(containers.to_string())
print(arrivals.to_string())
print(departures.to_string())
print(enumerations.to_string())
print(dispatching_lots)


def save_to_database():
    with pd.ExcelWriter(r"Database/Components.xlsx", mode='a', if_sheet_exists='replace') as writer:
        slots.to_excel(writer, sheet_name='Slots', index=False)
        containers.to_excel(writer, sheet_name='Containers', index=False)
    with pd.ExcelWriter(r"Database/Items.xlsx", mode='a', if_sheet_exists='replace') as writer:
        items.to_excel(writer, sheet_name='Items', index=False)
    with pd.ExcelWriter(r"Database/Orders.xlsx", mode='a', if_sheet_exists='replace') as writer:
        arrivals.to_excel(writer, sheet_name='Arrivals', index=False)
        departures.to_excel(writer, sheet_name='Departures', index=False)
    with open("Database/Temp/dispatching_temp.json", "w") as temp:
        json.dump(dispatching_lots, temp)


def update_arrivals():
    # Update Arrivals State
    mask = (arrivals['State'] == 'Scheduled') & (arrivals['Arrival Time'] < pd.Timestamp.now())
    arrivals.loc[mask, 'State'] = 'Arrived'

    mask = (arrivals['State'] == 'Arrived') & (arrivals['Dispatch Time'] < pd.Timestamp.now())
    arrivals.loc[mask, 'State'] = 'Dispatching'

    mask = arrivals['State'] == 'Dispatching'
    for cargo in arrivals.loc[mask, 'Items'].values:
        # print(f"Cargo: {cargo}")
        for lot in cargo:
            # print(f"Lot: {lot}")
            dispatching_names = [l['Name'] for l in dispatching_lots]
            if lot['Name'] not in dispatching_names:
                dispatching_lots.append(lot)
            else:
                dispatching_lots[dispatching_names.index(lot['Name'])]['Quantity'] += lot['Quantity']
    arrivals.loc[mask, 'State'] = 'Dispatched'
    print(f"\n{dispatching_lots = }")
    print(f"{len(dispatching_lots) = }")


def verify_dimensions(container: pd.Series, item_names: list, quantity: int):
    container_dimensions = [container['Length'], container['Width'], container['Height']]
    filled_volume = 0

    for item_name in item_names:
        item = items.loc[items['Name'] == item_name].iloc[0]
        item_dimensions = [item['Length'], item['Width'], item['Height']]
        # print(f"Item: {item['Name']}, Group volume: {item['Volume']*quantity}, Remaining Volume: {container['Volume'] - filled_volume}")

        container_dimensions_temp = container_dimensions
        item_dimensions_temp = item_dimensions

        # Verify that the container can fit the item.
        for i in range(len(container_dimensions)):
            # print(f"{container_dimensions_temp = },  {item_dimensions_temp = }")
            if max(container_dimensions_temp) >= max(item_dimensions_temp):
                container_dimensions_temp.remove(max(container_dimensions_temp))
                item_dimensions_temp.remove(max(item_dimensions_temp))

        # Verify that the container volume is enough to fit the wale quantity of items.
        filled_volume += item['Volume'] * quantity
        # print(f"{filled_volume = },  {container['Volume'] = },  {container['Volume'] >= filled_volume}, {len(container_dimensions_temp) == 0}")
        if not (len(container_dimensions_temp) == 0 and container['Volume'] >= filled_volume):
            return False
    return True


def select_container(item_names: list, total_quantity: int):
    # Select the first container that can fit the items.
    item_quantity = round(total_quantity / len(item_names))
    while True:
        print(f"{item_quantity = }")
        mask = pd.Series(False, containers.index)
        if item_quantity < 1:
            break
        mask = (
                (containers.apply(verify_dimensions, axis=1, args=(item_names, item_quantity))) &
                (containers['State'] == 'Free')
        )
        if any(mask):
            break
        else:
            item_quantity = round(item_quantity / 2)

    if not any(mask):
        print(f"No adequate container found. Selected items: {item_names}")
        return None

    container_index = containers.index[mask].values[0]
    print(f"\nFitting container ID: {containers.loc[container_index, 'ID']}\n")

    return container_index


def add_one_item(item: pd.Series, ci: int):
    """ Add one item to container.
    :param item: item
    :param ci: container index
    :return: filled container
    """
    if not (item['Name'] in [dispatching_lot['Name'] for dispatching_lot in dispatching_lots]):
        return False
    if containers.loc[ci, 'Item Types']:
        found = False
        for si, stored_item in enumerate(containers.loc[ci, 'Items']):
            if item['Name'] == stored_item['Name']:
                containers.loc[ci, 'Items'][si]['Quantity'] = stored_item['Quantity'] + 1
                found = True
                break
        if not found:
            containers.loc[ci, 'Items'].append({"Name": item['Name'], "Quantity": 1})
    else:
        containers.loc[ci, 'Items'].append({"Name": item['Name'], "Quantity": 1})

    containers.loc[ci, 'Item Types'] = len(containers.loc[ci, 'Items'])
    containers.loc[ci, 'Filled'] = containers.loc[ci, 'Filled'] + item['Volume']
    containers.loc[ci, 'Filling'] = math.ceil(containers.loc[ci, 'Filled'] / containers.loc[ci, 'Volume'] * 100)

    lot_index = [dispatching_lot['Name'] for dispatching_lot in dispatching_lots].index(item['Name'])
    dispatching_lots[lot_index]['Quantity'] -= 1
    if dispatching_lots[lot_index]['Quantity'] == 0:
        dispatching_lots.pop(lot_index)

    return True


def fill_with_many_items(items_names: list, ci: int, filling_percentage: int):
    while True:
        if len(items_names) == 0:
            print("\nContainer Partially Filled\n")
            break

        item_volumes = list(items.loc[items['Name'].isin(items_names), 'Volume'])
        remaining_volume = (filling_percentage - containers.loc[ci, 'Filling']) / 100 * containers.loc[ci, 'Volume']
        # print(f"\nRemaining Volume: {remaining_volume}")

        if all(remaining_volume < v for v in item_volumes):
            print("\nContainer Filled\n")
            break

        for i, item_name in enumerate(items_names):
            item = items.loc[items['Name'] == item_name].iloc[0]
            remaining_volume = (filling_percentage - containers.loc[ci, 'Filling']) / 100 * containers.loc[ci, 'Volume']
            if remaining_volume <= item['Volume']:
                items_names.pop(i)
                continue
            if item_name not in [dispatching_lot['Name'] for dispatching_lot in dispatching_lots]:
                items_names.pop(i)
                continue

            # print(f"Item: {item['Name']}, Volume: {item['Volume']}, Remaining Volume: {remaining_volume}")
            add_one_item(item, ci)

    print(f"\nFilled: {containers.loc[ci, 'Filled']}\nPercentage: {containers.loc[ci, 'Filling']}")
    return True


def are_similar(container: pd.Series, container_ref: pd.Series) -> bool:
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

    if mask.any():
        print(f"\nEqual container found.\n")
        similar_slots = containers.loc[mask, 'Slot'].values
        print(similar_slots)
        equal_slots_indexes = slots.index[slots['ID'].isin(similar_slots)].values

        # Find suitable slots
        # Not load close to a similar container
        path_distance_from_equal = 6
        while True:
            mask = pd.Series(True, slots.index)
            path_weights_to_avoid = []
            # print(mask.values)
            for esi in equal_slots_indexes:
                # print(f"\nSimilar slot: {slots.loc[esi, 'ID']} "
                #       f"Path Weight of similar slot: {slots.loc[esi, 'Path Weight']}")

                filter_max = slots.loc[esi, 'Path Weight'] + path_distance_from_equal
                filter_min = slots.loc[esi, 'Path Weight'] - path_distance_from_equal
                # print(f"Avoiding Weights from: {filter_min} to {filter_max}")
                path_weights_to_avoid.extend(list(range(filter_min, filter_max)))
                mask = mask & ((slots['Path Weight'] > filter_max) | (slots['Path Weight'] < filter_min))

            mask = mask & (slots['Type'] == container['Type']) & (slots['State'] == 'Free')
            path_weights_to_avoid = list(set(path_weights_to_avoid))
            print(f"\n{path_weights_to_avoid = }")
            # print(mask.values)
            if any(mask):
                break
            if path_distance_from_equal == 0:
                break
            path_distance_from_equal -= 1
            print(f"Decreasing path distance from equal to: {path_distance_from_equal}")

    else:
        print(f"\nNot equal container found.\nNo constrains on path weight")
        # Select all free slots compatible with the container
        mask = (slots['Type'] == container['Type']) & (slots['State'] == 'Free')

    # Select the slot with the lowest path weight
    if any(mask):
        print("Book a suitable slot while respecting the path weight constraints")
        slot_index = slots.loc[mask, 'Path Weight'].idxmin()
        slots.loc[slot_index, 'State'] = 'Booked'
        slots.loc[slot_index, 'Container'] = container['ID']

        print(f"\nBooked slot: {slots.loc[slot_index, 'ID']}")
        print(f"Path Weight: {slots.loc[slot_index, 'Path Weight']}")
        print(f"With container: {slots.loc[slot_index, 'Container']}\n")
        return slot_index

    print("No suitable slot found")
    return None


def dispatch_arrivals():
    """
The dispatch_arrivals function selects up to four lots from the dispatching_lots list and retrieves their names.
It then selects a container and fills it with the selected items, updating the container's state and priority.
The function books a slot for the container and updates the container's slot information in the database.
Finally, it prints the filled container and assigned slot.

    """
    # Select four items
    if len(dispatching_lots) < 4:
        return

    print(f"\nSelecting the four best items to load together")
    item_names = optimize_group(dispatching_lots, items, relations)
    # selected_lots = dispatching_lots[:4]
    # item_names = [lot['Name'] for lot in selected_lots]
    print(f"\n{item_names = }")

    # Select a suitable container
    container_index = select_container(item_names, 60)
    if container_index is None:
        return

    # Fill container with selected items
    fill_with_many_items(item_names, container_index, 95)

    containers.loc[container_index, 'State'] = 'Loading'
    containers.loc[container_index, 'Priority'] = containers.loc[:, 'Priority'].max() + 1
    containers.loc[container_index, 'Items Count'] = sum(
        [item['Quantity'] for item in containers.loc[container_index, 'Items']])

    # Book a slot for the container
    print(f"\nBooking a slot for the container: {containers.loc[container_index, 'ID']}")
    slot_index = book_free_slot(containers.loc[container_index])
    if slot_index is None:
        containers.loc[container_index, 'State'] = 'Waiting'
        print('Not slot index')
        return
    containers.loc[container_index, 'Slot'] = slots.loc[slot_index, 'ID']

    # Update Stored Quantity
    for item in containers.loc[container_index, 'Items']:
        item_index = items.loc[items['Name'] == item['Name']].index[0]
        items.loc[item_index, 'Stored Quantity'] += item['Quantity']

    # print(f"\nFilled container: {containers.loc[container_index, 'ID']} \nSlot: {slots.loc[slot_index, 'ID']}\n")
    return


def fulfill_departures():
    mask = (containers['State'] == 'Stored') & (containers['Priority'] == 0)
    # print(mask.values)
    if not any(mask):
        print("No containers for fulfillment")
        return

    # Select the 20 most urgent departures and their items
    departures.sort_values('Deadline')

    items_to_unload = []
    # print(departures.head(20).to_string())
    for d, departure in departures.head(20).iterrows():
        for lot in departure['Items']:
            items_to_unload_names = [l['Name'] for l in items_to_unload]
            if lot['Name'] in items_to_unload_names:
                index = items_to_unload_names.index(lot['Name'])
                items_to_unload[index]['Quantity'] += lot['Quantity']
            else:
                items_to_unload.append(lot.copy())

    items_to_unload_names = [l['Name'] for l in items_to_unload]
    print(f"\n{items_to_unload = }")

    unload_capacities = []  # {container_index: int, capacity: int, will_be_empty: bool}
    for c, container in containers.loc[mask].iterrows():
        container_quantity = 0
        data = {
            'Container Index': c,
            'Capacity': 0,
            'Will Be Empty': False
        }
        for lot in container['Items']:
            container_quantity += lot['Quantity']
            # Unloading capacity computed on items to unload
            if lot['Name'] in items_to_unload_names:
                index = items_to_unload_names.index(lot['Name'])
                data['Capacity'] += min(lot['Quantity'], items_to_unload[index]['Quantity'])
                # print(f"Container with capabilities {lot['Name'] = } and {lot['Quantity'] = } and {items_to_unload[index]['Quantity'] = }")

        if container_quantity == data['Capacity']:
            data['Will Be Empty'] = True

        unload_capacities.append(data)

    unloading_capacities_df = pd.DataFrame(unload_capacities).sort_values('Capacity', ascending=False)
    print(unloading_capacities_df)

    # Unload the container with the highest unloading capacity

    # Put the departures with those items in picking

    return


def picking():
    # Checks all Retrieved containers and picks the items necessary to fulfill the departures
    pass


def generate_load():
    mask = (containers['State'] == 'Loading') & (containers['Priority'] != 0)
    if not any(mask):
        print("No containers to load")
        return
    container_index = containers.loc[mask, 'Priority'].idxmin()
    # print(container_index)

    mask = (slots['ID'] == containers.loc[container_index, 'Slot']) & (slots['State'] == 'Booked')
    if not any(mask):
        print("No slot to load")
        return

    slot_index = slots.loc[mask].index[0]
    target = (slots.loc[slot_index, 'TargetX'], slots.loc[slot_index, 'TargetZ'])
    # print(target)

    commands_to_send.append(Command('Load', (0, 0), target, slots.loc[slot_index, 'ID']))
    containers.loc[container_index, 'Priority'] = 0


def generate_unload():
    mask = (containers['State'] == 'Unloading') & (containers['Priority'] != 0)
    if not any(mask):
        print("No containers to unload")
        return
    container_index = containers.loc[mask, 'Priority'].idxmin()
    # print(container_index)

    mask = (slots['ID'] == containers.loc[container_index, 'Slot']) & (slots['State'] == 'Occupied')
    if not any(mask):
        print("No slot to unload")
        return

    slot_index = slots.loc[mask].index[0]
    target = (slots.loc[slot_index, 'TargetX'], slots.loc[slot_index, 'TargetZ'])
    # print(target)

    commands_to_send.append(Command('Unload', target, (0, 0), slots.loc[slot_index, 'ID']))
    containers.loc[container_index, 'Priority'] = 0


def generate_commands():
    # if not commands_to_send:
    generate_load()
    generate_unload()
    print(f"\n{len(commands_to_send) = }")

    # Send commands to all handlers
    index = 0
    while index < len(commands_to_send):
        command = commands_to_send[index]
        sent = False
        for i, ch in enumerate(chs):
            print(f"Verify command: {command.to_string()} on PLC #{i}")
            if ch.verify_command(command):
                ch.add(command)
                commands_to_send.pop(index)
                print(f"Command added to handler: {ch.host}")
                sent = True
                break

        # Increment index only if the command was not sent
        if not sent:
            index += 1


def check_handlers():
    for ch in chs:
        ch.check()

        # Get commands done
        if ch.commands_done:
            commands_done.extend(ch.commands_done)
            ch.commands_done.clear()

    # Update database consistently with commands_done
    for command in commands_done:
        slot_id = command.id % 1000  # action multiplier
        slot_index = slots.loc[slots['ID'] == slot_id].index[0]
        container_index = containers.loc[containers['Slot'] == slot_id].index[0]

        if command.action == 'Load':
            slots.loc[slot_index, 'Items'].clear()
            slots.loc[slot_index, 'Items'].extend(containers.loc[container_index, 'Items'])
            slots.loc[slot_index, 'Items Count'] = sum([item['Quantity'] for item in slots.loc[slot_index, 'Items']])
            slots.loc[slot_index, 'Loads Count'] += 1
            slots.loc[slot_index, 'State'] = 'Occupied'

            containers.loc[container_index, 'Loads Count'] += 1
            containers.loc[container_index, 'State'] = 'Stored'

        elif command.action == 'Unload':
            slots.loc[slot_index, 'Items'].clear()
            slots.loc[slot_index, 'Items Count'] = 0
            slots.loc[slot_index, 'State'] = 'Free'

            containers.loc[container_index, 'State'] = 'Retrieved'

        print(f"\nSlot: {slots.loc[slot_index, 'ID']} updated. State: {slots.loc[slot_index, 'State']}")
        print(
            f"Container: {containers.loc[container_index, 'ID']} updated. State: {containers.loc[container_index, 'State']}")
        commands_done.remove(command)


def main():
    # Start main loop
    try:
        while True:
            print(f"\n\n\n------------ NEW ITERATION ------------")

            update_arrivals()
            dispatch_arrivals()

            fulfill_departures()
            picking()

            generate_commands()
            check_handlers()

            # save_to_database()
            # time.sleep(1)

    except KeyboardInterrupt:
        save_to_database()
        print("\nProgram terminated by user.")
        exit(0)


if __name__ == "__main__":
    main()
