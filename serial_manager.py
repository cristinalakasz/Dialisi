from PySide6.QtCore import QObject, Signal, Slot, Qt
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLabel
import time
import serial
import crcmod
import struct

crc8 = crcmod.mkCrcFun(0x107, initCrc=0x00, rev=False)
class SerialManager(QObject):
    data_received = Signal(int, bytes)
    ack_received = Signal(bool)

    def __init__(self, port_name, baud_rate):
        super().__init__()
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.running = True
        self.port = None

    @Slot()
    def start(self):
        try:
            self.port = serial.Serial(self.port_name, self.baud_rate, timeout=0.1)
            while self.running:
                if self.port.in_waiting > 0:
                    header = self.port.read(1)
                    self.data_received.emit(1, header)
        except Exception as e:
            print(f"Serial error: {e}")
    
    def send_package(self, ID_message, data):
        if not self.port or not self.port.is_open:
            return
    
    @Slot()
    def stop(self):
        self.running = False













