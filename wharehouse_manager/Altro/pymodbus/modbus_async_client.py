import asyncio
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.transaction import ModbusRtuFramer


def setup_async_client():
    """Setup async client."""
    client = AsyncModbusTcpClient(
        host='localhost',
        port=5020,
        framer=ModbusRtuFramer,
        timeout=3
    )
    return client


async def handle_holding_registers(client):
    """Read/write holding registers."""
    await client.write_register(1, 10)
    rr = await client.read_holding_registers(1, 1)
    print(rr.registers)

    await client.write_registers(1, [10] * 8)
    rr = await client.read_holding_registers(1, 8)
    print(rr.registers)

    arguments = {
        "read_address": 1,
        "read_count": 8,
        "write_address": 1,
        "write_registers": [256, 128, 100, 50, 25, 10, 5, 1],
    }
    await client.readwrite_registers(**arguments)
    rr = await client.read_holding_registers(1, 8)
    print(rr.registers)


async def run_async_client(client, modbus_calls=None):
    """Run async client."""
    await client.connect()
    print(f"connected: {client.connected}")
    if modbus_calls:
        await modbus_calls(client)
    await client.close()


if __name__ == "__main__":
    test_client = setup_async_client()
    asyncio.run(run_async_client(test_client, modbus_calls=handle_holding_registers))
