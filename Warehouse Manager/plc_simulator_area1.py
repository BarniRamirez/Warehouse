"""
This simulator, utilizing a specially created library,
replicates the behavior of the PLC running the warehouse PLC program developed for the automation lab.
"""

# Create a simulator with 3x3 slot targets starting from (1, 1)

from PLC import Simulator

Xn = 3  # Xn = number of x-axis targets
Zn = 3  # Zn = number of z-axis targets

from_x = 1  # from_x = starting x-axis target
from_z = 1  # from_z = starting z-axis target

available_targets = [(x, z) for x in range(from_x, Xn + 1) for z in range(from_z, Zn + 1)]
plc_simulator = Simulator('localhost', "Area1", available_targets, polling_time=0.5, execution_time=3)

try:
    plc_simulator.start()
except KeyboardInterrupt:
    plc_simulator.stop()
    exit(0)

