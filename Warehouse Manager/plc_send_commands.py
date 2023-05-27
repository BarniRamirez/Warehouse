import time
from PLC import CommandHandler

ch = CommandHandler("localhost", [1, 3], [1, 3])

# ch.add_load((1, 1), 1)
# ch.add_unload((0, 0), 2)
#
# ch.add_load((1, 2), 3)
# ch.add_load((1, 3), 4)
# ch.add_load((2, 1), 5)
# ch.add_load((2, 3), 6)
# ch.add_load((2, 2), 7)
#
# ch.add_unload((1, 2), 8)
# ch.add_unload((1, 3), 9)
# ch.add_unload((2, 1), 10)
# ch.add_unload((2, 3), 11)
#
# ch.add_load((1, 2), 12)
# ch.add_load((1, 3), 13)
# ch.add_load((2, 1), 14)
# ch.add_load((2, 3), 15)
# ch.add_load((2, 2), 16)
#
# ch.add_move((0, 0), (0, 0), 17)

try:
    while True:
        if not ch.check():
            print("Failed to check")
        time.sleep(1)
except KeyboardInterrupt:
    ch.save()
    print("Closed")
