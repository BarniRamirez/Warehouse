import asyncio
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
    ModbusSparseDataBlock,
)
from pymodbus.server import StartAsyncTcpServer
from pymodbus.transaction import ModbusRtuFramer


async def setup_server():
    datablock = ModbusSequentialDataBlock.create()

    slave_context = ModbusSlaveContext(di=datablock, co=datablock, hr=datablock, ir=datablock)
    server_context = ModbusServerContext(slaves=slave_context, single=True)  # Build data storage

    address = "localhost"  # nothing for 'localhost'
    port = 5020
    server = await StartAsyncTcpServer(
        context=server_context,  # Data storage
        framer=ModbusRtuFramer,  # The framer strategy to use
        address=(address, port),
        allow_reuse_address=True,  # allow the reuse of an address
        broadcast_enable=False,  # treat slave_id 0 as broadcast address,
    )
    return server


asyncio.run(setup_server(), debug=True)

