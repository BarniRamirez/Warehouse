import time
import json
from threading import Timer
from pyModbusTCP.server import ModbusServer, DataBank
from pyModbusTCP.client import ModbusClient
from pathlib import Path


class Command:
    def __init__(self, action: str | int, target_from: tuple, target_to: tuple, slot_id: int):
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

        if slot_id < 1000:
            self.id = slot_id + 1000 * (self.actions.index(self.action) + 1)
        else:
            self.id = slot_id

        self.target_from = target_from
        self.target_to = target_to

    def get_data(self):
        data = [
            self.id,
            self.actions.index(self.action) + 1,
            self.target_from[0],
            self.target_from[1],
            self.target_to[0],
            self.target_to[1]
        ]
        data = [int(x) for x in data]
        return data

    def get_slot_id(self):
        return self.id % 1000

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

        self.UNKNOWN = 0
        self.READY = 1
        self.OCCUPIED = 2
        self.NEW_COMMAND = 5
        self.COMMAND_DONE = 6
        self.COMMAND_ERROR = 10
        self.SYSTEM_ERROR = 11
        self.MAINTENANCE = 15

    def connect(self):
        if not self.client.host == self.host and self.client.port == self.port:
            self.client = ModbusClient(host=self.host, port=self.port, auto_open=True, debug=False)
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
            if self.state == self.NEW_COMMAND or self.state == self.COMMAND_DONE or self.state == self.COMMAND_ERROR:
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

            # print("Error in reading commands. Retrying...")
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

    def send_command_error(self, command: Command):
        registers = command.get_data()
        registers.append(self.COMMAND_ERROR)
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
    def __init__(self, host: str, name: str, targets: list, polling_time: float = 2):
        super().__init__(host, 502)  # Initialized on Modbus TCP port 502

        self.name = name
        self.targets = targets  # List of tuples of (x, z) coordinate

        self.commands = []
        self.commands_done = []
        self.commands_error = []
        self.history = []

        self.polling_time = polling_time

        self.file_path = Path(f"Database/{self.host}_{self.name}Handler.json")

        if not self.file_path.exists():
            # Create a new file with the default data structure
            data = {"commands": [], "history": [], "commands_done": [], "commands_error": []}
            with open(self.file_path, "w") as temp:
                json.dump(data, temp)
        else:
            with open(self.file_path, "r") as temp:
                data = json.load(temp)
            for register in data["commands"]:
                self.commands.append(self.registers_to_command(register))
            for register in data["history"]:
                self.history.append(self.registers_to_command(register))
            for register in data["commands_done"]:
                self.commands_done.append(self.registers_to_command(register))
            for register in data["commands_error"]:
                self.commands_error.append(self.registers_to_command(register))

    def save(self):
        commands_temp = []
        history_temp = []
        commands_done_temp = []
        commands_error_temp = []
        for command in self.commands:
            commands_temp.append(command.get_data())
        for command in self.history:
            history_temp.append(command.get_data())
        for command in self.commands_done:
            commands_done_temp.append(command.get_data())
        for command in self.commands_error:
            commands_error_temp.append(command.get_data())

        with open(self.file_path, "w") as temp:
            data = {
                "commands": commands_temp,
                "commands_done": commands_done_temp,
                "commands_error": commands_error_temp,
                "history": history_temp
            }
            print(data)
            json.dump(data, temp)

    def verify_target(self, target: tuple):
        if target in self.targets:
            return True

    def verify_command(self, command: Command):
        if command.action == "Load":
            return self.verify_target(command.target_to)
        if command.action == "Unload":
            return self.verify_target(command.target_from)
        if command.action == "Move":
            return self.verify_target(command.target_from) and self.verify_target(command.target_to)
        print(f"Verify command: Invalid command: {command.to_string()}")
        return False

    def add(self, command: Command):
        if self.verify_command(command):
            self.commands.append(command)
            return True
        return False

    def add_load(self, target_to: tuple, slot_id: int):
        print(f"Load: target {target_to}: commands: {len(self.commands)}")
        command = Command("Load", (0, 0), target_to, slot_id)
        if self.add(command):
            print(command.to_string())
            return command
        return None

    def add_unload(self, target_from: tuple, slot_id: int):
        command = Command("Unload", target_from, (0, 0), slot_id)
        if self.add(command):
            print(command.to_string())
            return command
        return None

    def add_move(self, target_from: tuple, target_to: tuple, slot_id: int):
        command = Command("Move", target_from, target_to, slot_id)
        if self.add(command):
            print(command.to_string())
            return command
        return None

    # Tasks
    def check(self):
        print(f"CommandHandler '{self.host}' is checking PLC state")
        if not self.update():
            print("\nFailed to update data")
            return False
        print(f"\nState: {self.state}")

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
            self.commands_done.append(self.command)
            self.set_state(self.UNKNOWN)

        if self.state == self.COMMAND_ERROR:
            print(f"\nCommand error. Please check the command: {self.command.to_string()}")
            print(f"Container: {self.command.get_slot_id()}")
            self.commands_error.append(self.command)
            self.set_state(self.UNKNOWN)

        if self.state == self.SYSTEM_ERROR:
            print(f"\nSystem error. Please check the error code: {self.error_code}")

        self.save()
        return True

    # Loop
    def run(self):
        self.check()
        Timer(self.polling_time, self.run).start()

    def start(self):
        print(f"Command handler {self.host} started")
        self.run()

    def stop(self):
        self.save()
        print(f"Command handler {self.host} stopped")


class Simulator(CommunicationModule):
    def __init__(self, host, name: str, targets: list, polling_time: float = 0.5, execution_time: float = 10):
        super().__init__(host, 502)

        self.name = name
        self.targets = targets  # List of tuples of (x, z) coordinate

        self.server = None
        self.data_bank = None

        self.commands = []
        self.commands_done = []

        self.polling_time = polling_time
        self.execution_time = execution_time
        self.idle = True

        self.file_path = Path(f"Database/{self.host}_{self.name}Simulator.json")

        if not self.file_path.exists():
            # Create a new file with the default data structure
            data = {"commands": [], "commands_done": []}
            with open(self.file_path, "w") as temp:
                json.dump(data, temp)
        else:
            with open(self.file_path, "r") as temp:
                data = json.load(temp)
            for register in data["commands"]:
                self.commands.append(self.registers_to_command(register))
            for register in data["commands_done"]:
                self.commands_done.append(self.registers_to_command(register))

    def save(self):
        commands_temp = []
        commands_done_temp = []
        for command in self.commands:
            commands_temp.append(command.get_data())
        for command in self.commands_done:
            commands_done_temp.append(command.get_data())
        with open(self.file_path, "w") as temp:
            data = {
                "commands": commands_temp,
                "commands_done": commands_done_temp
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

    def verify_target(self, target: tuple):
        if target in self.targets:
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

    # Temporized task
    def execute_next_command(self):
        if self.commands:
            print(f"\nExecuting command: {self.commands[0].to_string()}")
            self.send_command_done(self.commands[0])
            self.commands_done.append(self.commands[0])
            self.commands.pop(0)
            print(f"Command done.")

            if self.commands:
                print(f"Working command: {self.commands[0].to_string()}")
                Timer(self.execution_time, self.execute_next_command).start()
            else:
                self.idle = True

    # Task
    def check(self):
        if not self.update():
            print("\nFailed to update data")
            return

        if self.state == self.READY or self.state == self.OCCUPIED:
            if self.commands and self.idle:
                self.idle = False
                Timer(self.execution_time, self.execute_next_command).start()
                print(f"Working command: {self.commands[0].to_string()}")

        if self.state == self.NEW_COMMAND:
            print("\nNew command received")
            print(f"Received Command #{len(self.commands)}\n{self.command.to_string()}")
            if self.verify_command(self.command):
                self.commands.append(self.command)
                self.set_state(self.UNKNOWN)
            else:
                print("Check: New command not valid")
                self.send_command_error(self.command)

        if self.state == self.UNKNOWN:
            if len(self.commands) < 10 and not self.state == self.READY:
                self.set_state(self.READY)

            if not len(self.commands) < 10 and not self.state == self.OCCUPIED:
                self.set_state(self.OCCUPIED)

        return

    # Loop
    def run(self):
        print(self.state)
        self.check()
        self.save()
        Timer(self.polling_time, self.run).start()

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
