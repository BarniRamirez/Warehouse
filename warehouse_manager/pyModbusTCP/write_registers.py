import time
from pyModbusTCP.client import ModbusClient
import random

# init
client = ModbusClient(host='192.168.0.10', port=502, auto_open=True, debug=False)

# main loop
while True:
    registers = [0] * 8  # Initialization
    registers[0] = random.randint(1, 254)  # ID
    registers[6] = 1  # New Command

    action = random.randint(1, 3)
    registers[1] = action  # Action
    if action == 1:  # Load
        registers[4] = random.randint(1, 3)  # TargetX2 (to)
        registers[5] = random.randint(1, 3)  # TargetZ2 (to)
    elif action == 2:  # Unload
        registers[2] = random.randint(1, 3)  # TargetX  (from)
        registers[3] = random.randint(1, 3)  # TargetZ  (from)
    elif action == 3:  # Move
        registers[2] = random.randint(1, 3)  # TargetX  (from)
        registers[3] = random.randint(1, 3)  # TargetZ  (from)
        registers[4] = random.randint(1, 3)  # TargetX2 (to)
        registers[5] = random.randint(1, 3)  # TargetZ2 (to)

    print(registers)

    i = 0
    while True:
        i += 1
        if i == 10:
            print('max iteration reached')
            break
        if client.write_multiple_registers(0, registers):
            print(f"written {registers}")
            break
        else:
            print(f"error in writing commands")
    time.sleep(10)
