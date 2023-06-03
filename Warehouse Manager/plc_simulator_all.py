from PLC import Simulator

# Create a simulator with 20x10 slot targets starting from (1, 1)

xn = 20  # Xn = number of x-axis targets
zn = 10  # Zn = number of z-axis targets

from_x = 1  # from_x = starting x-axis target
from_z = 1  # from_z = starting z-axis target

available_targets = [(x, z) for x in range(from_x, xn + 1) for z in range(from_z, zn + 1)]
plc_simulator = Simulator('localhost', "all", available_targets, polling_time=0.5, execution_time=8)

try:
    plc_simulator.start()
except KeyboardInterrupt:
    plc_simulator.stop()
    exit(0)

