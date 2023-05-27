from PLC import Simulator

plc_simulator = Simulator('localhost')
try:
    plc_simulator.start()
except KeyboardInterrupt:
    plc_simulator.stop()

