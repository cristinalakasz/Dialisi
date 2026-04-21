from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLabel
import time

# Esempio conciso di QThread
class WorkerThread(QThread):
    update_signal = Signal(str)

    def run(self):
        for i in range(3):
            time.sleep(1)
            self.update_signal.emit(f"Lavoro {i+1}")

# ... (MainWindow setup omitted for brevity)
