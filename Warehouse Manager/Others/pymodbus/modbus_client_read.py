import time
import random
from pymodbus.client import ModbusTcpClient
from pymodbus.transaction import ModbusRtuFramer
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ExceptionResponse

client = ModbusTcpClient('localhost', port=5020, framer=ModbusRtuFramer)
client.connect()

while True:

    response = client.read_holding_registers(0, 8)

    if not response.isError() and not isinstance(response, ExceptionResponse):
        print(f"read {response.registers}")
    else:
        print(f"error in writing commands")
    time.sleep(2)

# client.write_coil(3, True)
# result = client.read_coils(0, 8)
# print(result.bits)
client.close()
