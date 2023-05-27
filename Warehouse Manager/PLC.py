import time
import json
from threading import Timer
from pyModbusTCP.server import ModbusServer, DataBank
from pyModbusTCP.client import ModbusClient
from pathlib import Path


class Command:
    def __init__(self, action: str | int, target_from: tuple, target_to: tuple, container_id: int):
        self.actions = [
            "Load",
            "Unload",
            "Move",
        ]

        if isinstance(action, int):
            if 0 <= action - 1 < len(self.actions):
                self.action = self.actions[action - 1]
            else:
                self.action = "Invalid"
        else:
            if action in self.actions:
                self.action = action
            else:
                self.action = "Invalid"

        if not(self.action in self.actions):
            print("Invalid action")
            raise ValueError(f"Invalid action: {self.action}")

        if container_id < 10000:
            self.id = container_id + 10000 * (self.actions.index(self.action) + 1)
        else:
            self.id = container_id

        self.target_from = target_from
        self.target_to = target_to

    def get_data(self):
        return [
            self.id,
            self.actions.index(self.action) + 1,
            self.target_from[0],
            self.target_from[1],
            self.target_to[0],
            self.target_to[1]
        ]

    def get_container_id(self):
        return self.id % 10000

    def to_string(self):
        if self.action == "Load":
            return f"{self.id}: {self.action}: {self.target_to}"
        if self.action == "Unload":
            return f"{self.id}: {self.action}: {self.target_from}"
        return f"{self.id}: {self.action}: {self.target_from} -> {self.target_to}"


class CommunicationModule:
    def __init__(self, host, port):
        self.client = ModbusClient()
        self.host = host
        self.port = port  # 502

        self.command: Command | None = None
        self.state = 0
        self.error_code = 0

        self.STATE_ADDRESS = 6
        self.ERROR_CODE_ADDRESS = 7

        self.READY = 0
        self.OCCUPIED = 1
        self.NEW_COMMAND = 2
        self.COMMAND_DONE = 3
        self.UNKNOWN = 4
        self.COMMAND_ERROR = 10
        self.SYSTEM_ERROR = 11
        self.MAINTENANCE = 15

    def connect(self):
        if not self.client.host == self.host and self.client.port == self.port:
            self.client = ModbusClient(host=self.host, port=self.port)
            if not self.client.open():
                raise ConnectionError(f"Failed to connect to {self.host}:{self.port}")

    def update(self):
        registers = self.read_registers(0, 8)
        if registers is None:
            return False
        if not any(registers):
            print("Empty Registers")
        else:
            self.state = registers[self.STATE_ADDRESS]
            self.error_code = registers[self.ERROR_CODE_ADDRESS]
            if self.state == self.NEW_COMMAND or self.state == self.COMMAND_DONE:
                self.command = CommandHandler.registers_to_command(registers)
        return True

    def read_registers(self, address, count):
        self.connect()

        # Read the registers from the specified address
        i = 0
        while True:
            i += 1
            if i == 10:
                print('Max iteration reached. Failed to read data.')
                return None

            registers = self.client.read_holding_registers(address, count)
            if registers:
                return registers

            print("Error in reading commands. Retrying...")
            time.sleep(0.05)

    def write_registers(self, address, registers):
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

            print("Error in writing commands. Retrying...")
            time.sleep(0.05)

    def set_state(self, state: int):
        return self.write_registers(self.STATE_ADDRESS, [state]) and self.update()

    def send_command_new(self, command: Command):
        registers = command.get_data()
        registers.append(self.NEW_COMMAND)
        return self.write_registers(0, registers)

    def send_command_done(self, command: Command):
        registers = command.get_data()
        registers.append(self.COMMAND_DONE)
        return self.write_registers(0, registers)

    @ staticmethod
    def registers_to_command(registers: list):
        if len(registers) < 6:
            print("Not enough registers to convert to a command.")
            return None
        try:
            command = Command(registers[1], (registers[2], registers[3]), (registers[4], registers[5]), registers[0])
        except ValueError:
            print("Invalid command.")
            return None
        return command


class CommandHandler(CommunicationModule):
    def __init__(self, host: str, xs: list, zs: list):
        super().__init__(host, 502)  # Initialized on Modbus TCP port 502

        self.xs = xs
        self.zs = zs

        self.commands = []
        self.history = []

        self.file_path = Path(f"Database/{self.host}_handler.json")

        if not self.file_path.exists():
            # Create a new file with the default data structure
            data = {"commands": [], "history": []}
            with open(self.file_path, "w") as temp:
                json.dump(data, temp)
        else:
            with open(self.file_path, "r") as temp:
                data = json.load(temp)
            for register in data["commands"]:
                print(register)
                self.commands.append(self.registers_to_command(register))
            for register in data["history"]:
                self.history.append(self.registers_to_command(register))

    def save(self):
        commands_temp = []
        history_temp = []
        for command in self.commands:
            commands_temp.append(command.get_data())
        for command in self.history:
            history_temp.append(command.get_data())
        with open(self.file_path, "w") as temp:
            data = {
                "commands": commands_temp,
                "history": history_temp
            }
            json.dump(data, temp)

    def verify_target(self, target: tuple):
        if target[0] < self.xs[0] or target[0] > self.xs[-1] or target[1] < self.zs[0] or target[1] > self.zs[-1]:
            print("Verify target: Invalid target")
            return False
        return True

    def verify_command(self, command: Command):
        if command.action == "Load":
            return self.verify_target(command.target_to)
        if command.action == "Unload":
            return self.verify_target(command.target_from)
        if command.action == "Unload":
            return self.verify_target(command.target_from) and self.verify_target(command.target_to)
        print(f"Verify command: Invalid command: {command.to_string()}")
        return False

    def add(self, command: Command):
        if self.verify_command(command):
            self.commands.append(command)
            return command
        return None

    def add_load(self, target_to: tuple, container_id: int):
        print(f"Load: target {target_to}: commands: {len(self.commands)}")
        command = Command("Load", (0, 0), target_to, container_id)
        if self.add(command):
            print(command.to_string())
            return command
        return None

    def add_unload(self, target_from: tuple, container_id: int):
        command = Command("Unload", target_from, (0, 0), container_id)
        if self.add(command):
            print(command.to_string())
            return command
        return None

    def add_move(self, target_from: tuple, target_to: tuple, container_id: int):
        command = Command("Move", target_from, target_to, container_id)
        if self.add(command):
            print(command.to_string())
            return command
        return None

    def check(self):
        if not self.update():
            print("\nFailed to update data")
            return False

        if self.state == self.READY and len(self.commands) != 0:
            command = self.commands[0]
            print(f"\nSending command: {command.to_string()}")
            if not self.send_command_new(command):
                print("Error in sending command")
                return False
            self.history.append(command)
            self.commands.pop(0)

        if self.state == self.OCCUPIED:
            print("\nPlc is occupied in other commands. Please wait")

        if self.state == self.COMMAND_DONE:
            print(f"\nCommand {self.command.to_string()} is done !!!")
            self.set_state(self.UNKNOWN)

        if self.state == self.COMMAND_ERROR:
            print(f"\nCommand error. Please check the command: {self.command.to_string()}")
            print(f"Container: {self.command.get_container_id()}")
            self.set_state(self.UNKNOWN)

        if self.state == self.SYSTEM_ERROR:
            print(f"\nSystem error. Please check the error code: {self.error_code}")

        return True


class Simulator(CommunicationModule):
    def __init__(self, host):
        super().__init__(host, 502)

        self.server = None
        self.data_bank = None

        self.commands = []
        self.history = []
        self.file_path = Path(f"Database/{self.host}_simulator.json")

        if not self.file_path.exists():
            # Create a new file with the default data structure
            data = {"commands": [], "history": []}
            with open(self.file_path, "w") as temp:
                json.dump(data, temp)
        else:
            with open(self.file_path, "r") as temp:
                data = json.load(temp)
            for register in data["commands"]:
                self.commands.append(self.registers_to_command(register))
            for register in data["history"]:
                self.history.append(self.registers_to_command(register))

        if len(self.commands):
            Timer(10, self.execute_command, [self.commands[0]]).start()

    def save(self):
        commands_temp = []
        history_temp = []
        for command in self.commands:
            commands_temp.append(command.get_data())
        for command in self.history:
            history_temp.append(command.get_data())
        with open(self.file_path, "w") as temp:
            data = {
                "commands": commands_temp,
                "history": history_temp
            }
            json.dump(data, temp)

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

    def start(self):
        self.initialize_server()
        self.initialize_registers()

        # Start the Modbus TCP server
        self.server.start()
        print("Modbus server started")

        self.run()

    def stop(self):
        self.save()
        self.server.stop()
        print("Modbus server stopped")

    def execute_command(self, command):
        if command in self.commands:
            print(f"\nExecuting command: {command.to_string()}")
            while True:
                if self.state == self.READY or self.state == self.OCCUPIED:
                    self.send_command_done(command)
                    break
                print(f"Waiting for plc to be in a valid state {self.state}")
                time.sleep(1)

            self.commands.remove(command)
            self.history.append(self.command)
            print(f"Command done.")

            if len(self.commands):
                Timer(10, self.execute_command, [self.commands[0]]).start()
            return True

        print("Command not found")
        return False

    def run(self):
        while True:
            if not self.update():
                print("\nFailed to update data")
                time.sleep(1)
                continue

            if self.state == self.NEW_COMMAND:
                print("\nNew command received")
                print(f"Received Command #{len(self.commands)}\n{self.command.to_string()}")
                if len(self.commands) == 0:
                    Timer(10, self.execute_command, [self.command]).start()
                self.commands.append(self.command)

                if not self.set_state(self.UNKNOWN):
                    print("\nFailed to set state")
                    time.sleep(1)
                    continue

            if self.state == self.UNKNOWN:
                if len(self.commands) < 10 and not self.state == self.READY:
                    self.set_state(self.READY)

                if not len(self.commands) < 10 and not self.state == self.OCCUPIED:
                    self.set_state(self.OCCUPIED)

            time.sleep(1)



