import pandas as pd
import random


slots = pd.read_excel(r"Database\Components.xlsx", sheet_name='Slots')
containers = pd.read_excel(r"Database\Components.xlsx", sheet_name='Containers')
items = pd.read_excel(r"Database\Items.xlsx", sheet_name='Items')
relations = pd.read_excel(r"Database\Items.xlsx", sheet_name='Relations')

print(items.to_string())
print(relations.to_string())
print(slots.to_string())
print(containers.to_string())










