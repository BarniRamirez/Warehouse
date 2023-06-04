AUTOMATED WAREHOUSE PROJECT

Politecnico di Milano a.a. 2022
AUTOMATION AND CONTROL LABORATORY, professor Gabriele Cazzulani
TEAM 15 WAREHOUSE - Barone Lorenzo, Bartoli Matteo, Brunacci Brigida, Guida Mario
---------------------------------------------------------------------------------


This file contains instructions to run the code and all the necessary libraries.

*INSTRUCTIONS*

For running a simulation with the warehouse manager follow the steps:
1.initialize the database running the reset_database.py file
2.run create_arrivals_random.py to generate a simulated arrival order
3.run create_departures.py to generate simulated departures order
4.run WarehouseManager.py
5.quickly run also plc_simulator_all.py to simulate a PLC with all targets awailable

You can check the database files whenever you desire after stopping the warehouse manager and plc simulator, 
if you want to continue the simulation make sure to restart from point 4.

If you want to run a new simulation delete files in the "Temp" folder and follow steps from 1.

*PY modules*

Install the following py libraries: pyModbusTCP, threading, numpy, pandas, mip.