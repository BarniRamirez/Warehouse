from pyModbusTCP.client import ModbusClient
import time


client = ModbusClient(host='192.168.1.50', port=502, auto_open=True, auto_close=False)


# main read loop
while True:
    # read 8 registers at address 0, store result in regs list
    regs_l = client.read_holding_registers(0, 8)

    # if success display registers
    if regs_l:
        print('reg ad #0 to 7: %s' % regs_l)
    else:
        print('unable to read registers')

    # sleep 2s before next polling
    time.sleep(2)

