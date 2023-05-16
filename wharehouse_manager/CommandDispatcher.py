import pandas as pd
import random

items = pd.read_excel("Database/Items.xlsx", sheet_name="items")
relations = pd.read_excel("Database/Items.xlsx", sheet_name="relations")



print(items.to_string())
print(relations.to_string())

print(relations.iloc[0, 1])

# for i in range(0, 50):
#     items.loc[i, 'Sn'] = str(random.randint(1000000000000,9999999999999))
#
# print(items.to_string())
#
# with pd.ExcelWriter('Database/Items.xlsx', mode='a', if_sheet_exists='replace') as writer:
#     items.to_excel(writer, sheet_name='items_sn', index=False)
