import serial
import crcmod

crc8 = crcmod.mkCrcFun(0x107, initCrc=0x00, rev=False)

def send_package(port, ID_message, data):
    header = b'\xAA'
    ID_message_bytes = bytes([ID_message])
    data_length = bytes([len(data)])
    data_bytes = bytes(data)
    CRC = crc8(ID_message_bytes + data_length + data_bytes)
    CRC_byte = bytes([CRC])
    package = header + ID_message_bytes + data_length + data_bytes + CRC_byte
    port.write(package)

def receive_package(port):
    while True:
        header = port.read(1)
        if header == b'\xaa':
            ID_message = port.read(1)
            data_length = port.read(1)
            break;
    data = port.read(ord(data_length))
    CRC_received = port.read(1)
    CRC_calculated = crc8(ID_message + data_length + data)

    if CRC_received == CRC_calculated:
        print(f"Pacchetto ricevuto correttamente: {data.hex().upper()}")
    else:
        print("Errore di integrità del pacchetto")
