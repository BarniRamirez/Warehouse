"""
Test PLC sending commands through modbus.
Targets compatible with Warehouse test machine in automation lab.
Use localhost for testing.
"""
from PLC import CommandHandler

# Area dimensions
Xn = 3
Zn = 3

# Command Handler initialization
available_targets = [(x, z) for x in range(1, Xn + 1) for z in range(1, Zn + 1)]
ch = CommandHandler(host="localhost", name="local_test", targets=available_targets, polling_time=2)

# Commands to send
ch.add_load((1, 1), 1)
ch.add_load((2, 2), 22)
ch.add_load((2, 1), 2)
ch.add_unload((1, 2), 21)
ch.add_move((2, 2), (1, 2), 22)

ch.delete(1002)  # Delete the third load

ch.add_unload((2, 1), 2)
ch.add_load((2, 1), 2)
ch.add_unload((1, 1), 1)
ch.add_load((1, 1), 1)
ch.add_unload((1, 2), 22)
ch.add_load((1, 2), 22)

# Start the command handler
ch.start()
