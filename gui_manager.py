import sys
import struct
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit
from serial_manager import SerialManager
from protocol import MessageID, ProgramState, PAYLOAD_FORMATS

class GUIManager(QWidget):
    request_send = Signal(int, object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Communication")
        self.setGeometry(100, 100, 400, 300)
        self.layout = QVBoxLayout()

        self.btn_on = QPushButton("ON")
        self.btn_on.clicked.connect(self.send_on)
        self.layout.addWidget(self.btn_on)

        self.btn_off = QPushButton("OFF")
        self.btn_off.clicked.connect(self.send_off)
        self.layout.addWidget(self.btn_off)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.layout.addWidget(self.console)

        self.setLayout(self.layout)
        
        self.thread = QThread()
        self.worker = SerialManager("/dev/cu.usbserial-110", 115200)
        self.worker.moveToThread(self.thread)

        self.request_send.connect(self.worker.send_package, Qt.DirectConnection)
        self.thread.started.connect(self.worker.start)
        self.worker.data_received.connect(self.print_data)
        self.worker.ack_received.connect(self.handle_ack)
        self.worker.error_occurred.connect(self.handle_error)

        self.thread.start()

    def send_on(self):
        self.console.append("Sent: PROGRAM_PRINCIPAL")
        self.request_send.emit(MessageID.M_PROGRAM, ProgramState.P_PRINCIPAL)

    def send_off(self):
        self.console.append("Sent: PROGRAM_STOP")
        self.request_send.emit(MessageID.M_PROGRAM, ProgramState.P_STOP)
    
    @Slot(int, bytes)
    def print_data(self, ID_message, data_bytes):
        try:
            msg_name = MessageID(ID_message).name
            pf = PAYLOAD_FORMATS[ID_message]
            if pf:
                valore = struct.unpack(pf, data_bytes)[0]
            else:
                valore = "Nessun payload"
            self.console.append(f"Received data from ID {msg_name}: {valore}")
        except Exception as e:
            self.console.append(f"Received data from ID {msg_name}: {data_bytes.hex()}")
    
    @Slot(bool)
    def handle_ack(self, ack):
        self.console.append(f"ACK: {ack}")
    
    @Slot(str)
    def handle_error(self, error_message):
        self.console.append(f"Error: {error_message}")
    
    def closeEvent(self, event):
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GUIManager()
    window.show()
    sys.exit(app.exec())