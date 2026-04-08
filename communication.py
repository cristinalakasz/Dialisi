import serial
import crcmod

crc16 = crcmod.Crc16(0x11021, initCrc=0xFFFF, rev=False)

def send_package(port, ID_message, data, CRC):
    header = bytes([0xAA])
    data_length = bytes([len(data)])
    data_bytes = bytes(data)
    CRC = bytes([crc16(data_bytes)])
    package = header + ID_message + data_length + data_bytes + CRC
    port.write(package)
