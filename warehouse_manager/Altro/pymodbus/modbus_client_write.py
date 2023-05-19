import time
import random
from pymodbus.client import ModbusTcpClient
from pymodbus.transaction import ModbusRtuFramer
from pymodbus.pdu import ExceptionResponse

client = ModbusTcpClient('192.168.0.10', port=1201, framer=ModbusRtuFramer)
client.connect()

while True:
    registers = [
        random.randint(1, 254),
        random.randint(1, 3),
        random.randint(1, 3),
        random.randint(1, 3),
        0, 0, 0, 0
    ]
    registers[4] = random.randint(1, 3) if registers[1] == 3 else 0
    registers[5] = random.randint(1, 3) if registers[1] == 3 else 0

    response = client.write_registers(0, registers)

    if not response.isError() and not isinstance(response, ExceptionResponse):
        print(f"written {registers}")
        # , registers count: {response.count}, starting address: {response.address}
    else:
        print(f"error in writing commands")
    time.sleep(5)

client.close()


# client.write_coil(3, True)
# result = client.read_coils(0, 8)
# print(result.bits)
