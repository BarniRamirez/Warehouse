import json
from pathlib import Path

host = "localhost"
file_path = Path(f"Database/{host}_simulator.json")

data = {"commands": [], "commands_done": []}
with open(file_path, "w") as temp:
    json.dump(data, temp)

# import threading
#
#
# def my_function():
#     print("Hello")
#
#
# timer = threading.Timer(5.0, my_function)
# timer.start()
#
#
# while True:
#     if timer.is_alive():
#         print("Timer is alive")


# import numpy as np
# import pandas as pd
# import mip
# import ast
#
# slots = pd.read_excel(r"Database\Components.xlsx", sheet_name='Slots')
# slots['Items'] = slots['Items'].apply(ast.literal_eval)
#
#
# print(slots.loc[slots['Area'] == 1].apply(lambda row: (row['TargetX'], row['TargetZ']), axis=1).tolist())
#
#
# command = []
# if command:
#     print("hhvh")




# print(list(range(1, 10)))
#
# actions = ['eat', 'sleep', 'repeat']
# action = 0
#
# print(not(action in list(range(1, len(actions) + 1))))