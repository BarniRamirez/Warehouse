import time

from pyModbusTCP.client import ModbusClient


class PLCHandler:
    def __init__(self, host, port, xn, zn):
        self.client = ModbusClient()
        self.host = host
        self.port = port  # 502

        self.xn = xn
        self.zn = zn
        self.state = 0
        self.working_command = 0
        self.error_code = 0

        self.commands = []
        self.history = []

        self.STATE_READY = 0
        self.STATE_OCCUPIED = 1
        self.STATE_COMMAND_ERROR = 10
        self.STATE_SYSTEM_ERROR = 11

    def connect(self):
        if not self.client.host == self.host and self.client.port == self.port:
            self.client = ModbusClient(host=self.host, port=self.port)
            if not self.client.open():
                raise ConnectionError(f"Failed to connect to {self.host}:{self.port}")

    def check(self):
        self.connect()
        if not self.update_state():
            return False

        if self.state == self.STATE_READY and len(self.commands) != 0:
            command = self.commands[0]
            print(f"Sending command: {command}")
            if not self.write(0, command):
                return False
            self.history.append(command)
            self.commands.pop(0)
            return True

        if self.state == self.STATE_OCCUPIED:
            print("Plc is occupied in other commands. Please wait")
            return False

        if self.state == self.STATE_COMMAND_ERROR:
            print(f"Command error. Please check the command id: {self.working_command}")
            return False

        if self.state == self.STATE_SYSTEM_ERROR:
            print(f"System error. Please check the error code: {self.error_code}")
            return False

        return True

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

    def add_load(self, target: tuple, container_id: int):
        command = [
            container_id + 10000,  # Command ID
            1,  # Load command
            0,  # Target X
            0,  # Target Y
            int(target[0]),  # Target X2
            int(target[1]),  # Target Y2
            1,  # New Command
        ]

        self.commands.append(command)
        print(command)
        return command

    def add_unload(self, target: tuple, container_id: int):
        command = [
            container_id + 20000,  # Command ID
            1,  # Unload command
            int(target[0]),  # Target X
            int(target[1]),  # Target Y
            0,  # Target X2
            0,  # Target Y2
            1,  # New Command
        ]

        self.commands.append(command)
        print(command)
        return command

    def add_move(self, target: list, container_id: int):
        command = [
            container_id + 30000,  # Command ID
            3,  # Move command
            int(target[0][0]),  # Target X
            int(target[0][1]),  # Target Y
            int(target[1][0]),  # Target X2
            int(target[1][1]),  # Target Y2
            1,  # New Command
        ]

        self.commands.append(command)
        print(command)
        return command


if __name__ == "__main__":
    plc = PLCHandler("localhost")
    if not plc.check():
        print("Failed to check")
        exit(1)
    plc.add_load((0, 0), 1)
    plc.add_unload((0, 0), 1)
    plc.add_move([[0, 0], [0, 0]], 1)

    while True:
        if not plc.check():
            print("Failed to check")
        print(f"State: {plc.state}")
        time.sleep(1)



