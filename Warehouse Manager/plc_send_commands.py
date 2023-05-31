import time
from PLC import CommandHandler

available_targets = [(x, z) for x in range(1, 4) for z in range(1, 4)]
ch = CommandHandler("192.168.0.10", "test", available_targets)

ch.add_load((1, 1), 1)
ch.add_load((2, 2), 22)
ch.add_load((2, 1), 2)
ch.add_unload((1, 2), 21)
ch.add_move((2, 2), (1, 2), 22)

ch.add_unload((2, 1), 2)
ch.add_load((2, 1), 2)
ch.add_unload((1, 1), 1)
ch.add_load((1, 1), 1)
ch.add_unload((1, 2), 22)
ch.add_load((1, 2), 22)

try:
    ch.start()
except KeyboardInterrupt:
    ch.stop()
    exit(0)
