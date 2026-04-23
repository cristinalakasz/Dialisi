import serial
import crcmod
import struct
from PySide6.QtCore import QThread, QObject, Signal, Slot
from protocol import MessageID, PAYLOAD_FORMATS

crc8 = crcmod.mkCrcFun(0x107, initCrc=0x00, rev=False)

class SerialManager(QObject):
    data_received = Signal(int, bytes)
    ack_received = Signal(bool)
    error_occurred = Signal(str)

    def __init__(self, port_name, baud_rate=115200):
        super().__init__()
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.running = True
        self.port = None

        self.ID_message_back = 0
        self.data_back = b'\x00'
        self.retry_count = 0
        self.MAX_RETRIES = 3

    @Slot()
    def start(self):
        try:
            self.port = serial.Serial(self.port_name, self.baud_rate, timeout=0.1)
            while self.running:
                QThread.msleep(1)
                header = self.port.read(1)
                if header == b'\xAA':
                    ID_message_bytes = self.port.read(1)
                    data_length_bytes = self.port.read(1)
                    if not ID_message_bytes or not data_length_bytes: continue

                    ID_message = ID_message_bytes[0]
                    data_length = data_length_bytes[0]
                    payload_bytes = self.port.read(data_length)
                    if (len(payload_bytes) != data_length): continue

                    crc_bytes = self.port.read(1)
                    if not crc_bytes: continue

                    CRC = crc8(ID_message_bytes + data_length_bytes + payload_bytes)
                    if CRC == crc_bytes[0]:
                        if ID_message == MessageID.M_ACK:
                            self.ack_received.emit(True)
                            self.retry_count = 0
                        elif ID_message == MessageID.M_NACK:
                            self.ack_received.emit(False)
                            if self.retry_count < self.MAX_RETRIES:
                                self.retry_count += 1
                                self.send_package(self.ID_message_back, self.data_back)
                            else:
                                self.error_occurred.emit(f"Max retries reached for ID_message: {self.ID_message_back}, data: {self.data_back}")
                                self.retry_count = 0
                        else:
                            self.data_received.emit(ID_message, payload_bytes)
                            self.send_package(MessageID.M_ACK, None)
                    else:
                        self.send_package(MessageID.M_NACK, None)
        except serial.SerialException as e:
            self.error_occurred.emit(str(e))
        finally:
            if self.port and self.port.is_open:
                self.port.close()
    
    @Slot(int, object)
    def send_package(self, ID_message, data):
        if not self.port or not self.port.is_open:
            return
        try:
            pf = PAYLOAD_FORMATS[ID_message]
            data_bytes = struct.pack(pf, data) if pf else b''
        except KeyError:
            self.error_occurred.emit(f"Error: ID {ID_message} not recognized.")
            return
        except struct.error:
            self.error_occurred.emit(f"Error: Invalid data format for ID {ID_message}.")
            return
        
        if ID_message not in [MessageID.M_ACK, MessageID.M_NACK]:
            self.ID_message_back = ID_message
            self.data_back = data
            self.retry_count = 0

        header = b'\xAA'
        ID_message_bytes = bytes([ID_message])
        data_length = bytes([len(data_bytes)])
        CRC = crc8(ID_message_bytes + data_length + data_bytes)
        CRC_byte = bytes([CRC])
        package = header + ID_message_bytes + data_length + data_bytes + CRC_byte
        self.port.write(package)
        self.port.flush()

    @Slot()
    def stop(self):
        self.running = False