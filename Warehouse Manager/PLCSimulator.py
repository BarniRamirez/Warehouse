import time
import json
from pyModbusTCP.server import ModbusServer, DataBank
from pyModbusTCP.client import ModbusClient


class PLCSimulator:
    def __init__(self, host, port=502):
        self.host = host
        self.port = port
        self.server = None
        self.client = ModbusClient()
        self.data_bank = None

        self.state = 0
        self.working_command = 0
        self.error_code = 0

        with open(r"Database/commands_temp.json", "r") as temp:
            self.commands = json.load(temp)
        self.history = []

        self.STATE_READY = 0
        self.STATE_OCCUPIED = 1
        self.STATE_COMMAND_ERROR = 10
        self.STATE_SYSTEM_ERROR = 11

    def initialize_server(self):
        self.server = ModbusServer(host=self.host, port=self.port, no_block=True)
        print(f"Modbus server initialized at {self.host}:{self.port}")

    def initialize_registers(self):
        self.data_bank = DataBank()

        # Define your registers and their initial values
        registers = [0x0000] * 100  # Total 100 registers

        # Set the initial register values
        self.data_bank.set_words(0, registers)
        print("Registers initialized with initial values")

    def connect(self):
        if not self.client.host == self.host and self.client.port == self.port:
            self.client = ModbusClient(host=self.host, port=self.port)
            if not self.client.open():
                raise ConnectionError(f"Failed to connect to {self.host}:{self.port}")

    def start(self):
        self.initialize_server()
        self.initialize_registers()

        # Start the Modbus TCP server
        self.server.start()
        print("Modbus server started")

        self.run()

    def stop(self):
        with open("Database/commands_temp.json", "w") as temp:
            json.dump(self.commands, temp)
        self.server.stop()
        print("Modbus server stopped")

    def update_state(self):
        self.connect()

        # Read the state from the appropriate address
        registers = self.client.read_holding_registers(6, 3)
        if not registers:
            return False
        print(f"Read Register: {registers}")

        self.state = registers[0]
        self.working_command = registers[1]
        self.error_code = registers[2]
        return True

    def write(self, address, registers):
        self.connect()

        # Write the registers to the specified address
        i = 0
        while True:
            i += 1
            if i == 10:
                print('Max iteration reached. Failed to write data.')
                return False
            if self.client.write_multiple_registers(address, registers):
                print(f"Successfully written registers: {registers}")
                return True
            else:
                print("Error in writing commands. Retrying...")

    def read_command(self):
        self.connect()

        # Read the command from the appropriate address
        registers = self.client.read_holding_registers(0, 6)
        if not registers:
            return False
        print(f"Read Register: {registers}")
        command = registers[:6]
        return command

    def run(self):
        while True:
            self.update_state()
            if self.state == self.STATE_OCCUPIED:
                self.commands.append(self.read_command())
                if self.write(6, [self.STATE_READY, 0, 0]):
                    print("New command received")

            print(f"Received Command #{len(self.commands)}")
            print(self.commands)

            print(self.state)
            print(self.working_command)
            print(self.error_code)

            time.sleep(1)


if __name__ == '__main__':
    simulator = PLCSimulator('localhost')
    try:
        simulator.start()
    except KeyboardInterrupt:
        simulator.stop()

