"""
Resets the database to the default database.
"""

import pandas as pd
import ast
import json

# Import default database

slots = pd.read_excel(r"Defaults/Components_default.xlsx", sheet_name='Slots')
slots['Items'] = slots['Items'].apply(ast.literal_eval)
containers = pd.read_excel(r"Defaults/Components_default.xlsx", sheet_name='Containers')
containers['Items'] = containers['Items'].apply(ast.literal_eval)

items = pd.read_excel(r"Defaults/Items_default.xlsx", sheet_name='Items')
relations = pd.read_excel(r"Defaults/Items_default.xlsx", sheet_name='Relations')

# Reset warehouse database

with pd.ExcelWriter(r"Database/Components.xlsx", mode='a', if_sheet_exists='replace') as writer:
    slots.to_excel(writer, sheet_name='Slots', index=False)
    containers.to_excel(writer, sheet_name='Containers', index=False)

with pd.ExcelWriter(r"Database/Items.xlsx", mode='a', if_sheet_exists='replace') as writer:
    items.to_excel(writer, sheet_name='Items', index=False)
    relations.to_excel(writer, sheet_name='Relations', index=False)

with open("Database/Temp/dispatching_temp.json", "w") as temp:
    json.dump([], temp)

with open("Database/Temp/commands_temp.json", "w") as temp:
    json.dump([], temp)
