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
    CRC = crc8(ID_message_bytes + data_length + data_bytes)
    CRC_byte = bytes([CRC])
    package = header + ID_message_bytes + data_length + data_bytes + CRC_byte
    port.write(package)

def receive_package(port):
    while True:
        header = port.read(1)
        if header == b'\xAA':
            ID_message_bytes = port.read(1)
            data_length_bytes = port.read(1)
            ID_message = ID_message_bytes[0]
            data_length = data_length_bytes[0]
            if not ID_message_bytes or not data_length_bytes: continue
            payload_bytes = port.read(data_length)
            if (len(payload_bytes) != data_length): continue
            crc_bytes = port.read(1)
            if not crc_bytes: continue
            CRC = crc8(ID_message_bytes + data_length_bytes + payload_bytes)
            if CRC == crc_bytes[0]:
                if ID_message == 0xFA:
                    ack = True
                    print(f"ACK: {ack}")
                elif ID_message == 0xFB:
                    ack = False
                    print(f"ACK: {ack}")
                else:
                    print(f"header: {header.hex().upper()}, Received message ID: {ID_message_bytes.hex().upper()}, Data length: {data_length_bytes.hex().upper()}, Data: {payload_bytes.hex().upper()}")
                    send_package(port, 0xFA, [])
            else:
                send_package(port, 0xFB, [])
                print("CRC error")

if __name__ == "__main__":
    try:
        receive_package(port)
    except KeyboardInterrupt:
        port.close()
