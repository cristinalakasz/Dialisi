from PySide6.QtCore import QObject, Signal, Slot, Qt, QThread
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLabel
from serial_manager import SerialManager

class GUIManager(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.label = QLabel("In attesa...", self)
        self.button = QPushButton("Avvia Thread", self)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.start_thread)

def start_thread(self):
            # 2. Crea il thread e il worker
            self.thread = QThread()
            self.worker = SerialManager(self.port_name, self.baud_rate)

            # 3. Sposta il worker nel thread
            self.worker.moveToThread(self.thread)

            # 4. Connetti i segnali
            self.worker.data_received.connect(self.update_label, type=Qt.DirectConnection)
            self.thread.started.connect(self.worker.start)
            self.worker.ack_received.connect(self.thread.quit)
            self.worker.ack_received.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.progress.connect(self.send_package, )

            # 5. Avvia
            self.thread.start()
            self.button.setEnabled(False)
            self.thread.finished.connect(lambda: self.button.setEnabled(True))