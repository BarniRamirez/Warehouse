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









# print(len(relations.loc[:, 'Product']))
#
# for i in range(0, 50):  # Row
#     for j in range(0, 50):
#         if i < j+1:
#             relations.iloc[j, i+1] = relations.iloc[i, j+1]
#
# print(relations.to_string())
#
# with pd.ExcelWriter(r"C:\Users\pc\Desktop\Items_def.xlsx", mode='a', if_sheet_exists='replace') as writer:
#     relations.to_excel(writer, sheet_name='relations', index=False)
