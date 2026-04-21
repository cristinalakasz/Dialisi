import serial
import crcmod
import struct

crc8 = crcmod.mkCrcFun(0x107, initCrc=0x00, rev=False)
port = serial.Serial("/dev/cu.usbserial-110", 115200, timeout=0.1)

def send_package(port, ID_message, data):
    if not port or not port.is_open:
        print("Error: 0")
        return
    if isinstance(data, float):
        data_bytes = struct.pack('<f', data)
    elif isinstance(data, int):
        data_bytes = bytes([data])
    elif isinstance(data, (list, tuple)):
        data_bytes = bytes(data)
    else:
        print("Error: 2")
        return
    
    header = b'\xAA'
    ID_message_bytes = bytes([ID_message])
    data_length = bytes([len(data)])
    data_bytes = bytes(data)
    CRC = crc8(ID_message_bytes + data_length + data_bytes)
    CRC_byte = bytes([CRC])
    package = header + ID_message_bytes + data_length + data_bytes + CRC_byte
    print(f"DEBUG: {package.hex().upper()}")
    port.write(package)

def receive_package(port):
    while True:
        header = port.read(1)
        if header == b'\xaa':
            ID_message_bytes = port.read(1)
            data_length_bytes = port.read(1)
            ID_message = ID_message_bytes[0]
            data_length = data_length_bytes[0]
            if not ID_message_bytes or not data_length_bytes: continue
            payload = port.read(data_length)
            if len(payload) != data_length: continue
            crc_bytes = port.read(1)
            if not crc_bytes: continue
            CRC = crc8(ID_message + data_length + payload)
            if CRC == crc_bytes[0]:
                if ID_message == 0xFA:
                    print("ACK")
                    ack = True
                elif ID_message == 0xFB:
                    print("NACK")
                    ack = False
                else:
                    send_package(port, 0xFA, [])
            else:
                send_package(port, 0xFB, [])