import sys
import struct

from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                               QSlider, QLabel, QHBoxLayout, QCheckBox, QSplitter, 
                               QMenu, QMessageBox, QFrame, QWidgetAction)

import pyqtgraph as pg

from serial_manager import SerialManager
from protocol import MessageID, PAYLOAD_FORMATS, ProgramState, STATE_INFO

# Style
DARK_THEME = """
QWidget {
    background-color: #0D0D12;
    color: #00E5FF;
    font-family: 'Helvetica Neue', Arial;
    font-size: 13px;
}
QLabel { color: #A0A0B0; font-weight: bold; }
QLabel#Title { color: #00E5FF; font-size: 18px; font-weight: 900; letter-spacing: 2px; }
QLabel#ValueLabel { color: #00E5FF; font-family: 'Menlo', 'Monaco'; font-size: 14px; }

QSlider::groove:horizontal {
    border: 1px solid #1F1F2E; height: 4px; background: #1A1A24; border-radius: 2px;
}
QSlider::sub-page:horizontal {
    background: #00E5FF; border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #FFFFFF; border: 2px solid #00E5FF; width: 12px; margin: -5px 0; border-radius: 6px;
}

QPushButton {
    background-color: #161622; border: 1px solid #00E5FF; color: #00E5FF; 
    padding: 10px; border-radius: 4px; font-weight: bold; font-size: 14px;
}
QPushButton:hover { background-color: #00E5FF; color: #0D0D12; }
QPushButton::menu-indicator { image: none; }

QCheckBox { spacing: 8px; }
QCheckBox::indicator { width: 18px; height: 18px; border: 1px solid #00E5FF; border-radius: 4px; background: #161622; }
QCheckBox::indicator:checked { background: #00E5FF; }

QMenu { background-color: #161622; color: #00E5FF; border: 1px solid #00E5FF; }
QMenu::item { padding: 8px 20px; }
QMenu::item:selected { background-color: #00E5FF; color: #0D0D12; }

QSplitter::handle { background-color: #1F1F2E; }

QToolTip {
    background-color: #0D0D12;
    color: #00E5FF;
    border: 1px solid #00E5FF;
    border-radius: 4px;
    padding: 6px;
    font-family: 'Helvetica Neue', Arial;
    font-size: 13px;
}
"""

class GUIManager(QWidget):
    request_send = Signal(int, object)
    ratio_dd = 0.8
    fluid_velocity = 0.2
    sampling_rate = 0.1

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard")
        self.resize(1400, 900)

        # Main Layout and Splitter
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)

        # Left Panel: Controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(20)
        controls_layout.setAlignment(Qt.AlignTop)

        # Title
        title = QLabel("SYSTEM CONTROL")
        title.setObjectName("Title")
        controls_layout.addWidget(title)

        # Sliders
        self.val_ratio = QLabel(f"{int(self.ratio_dd * 100)}%")
        self.val_ratio.setObjectName("ValueLabel")
        self.slider_ratio = QSlider(Qt.Horizontal)
        self.slider_ratio.setRange(0, 100)
        self.slider_ratio.setValue(int(self.ratio_dd * 100))
        self.slider_ratio.valueChanged.connect(lambda val: self.update_slider(self.val_ratio, val, MessageID.M_RATIO_DD, "%"))
        controls_layout.addLayout(self.make_slider_row("Ratio Dialysed/Dye:", self.slider_ratio, self.val_ratio))

        self.val_vel = QLabel(f"{int(self.fluid_velocity * 100)} mL/s")
        self.val_vel.setObjectName("ValueLabel")
        self.slider_velocity = QSlider(Qt.Horizontal)
        self.slider_velocity.setRange(0, 100)
        self.slider_velocity.setValue(int(self.fluid_velocity * 100))
        self.slider_velocity.valueChanged.connect(lambda val: self.update_slider(self.val_vel, val, MessageID.M_FLUID_VELOCITY, " mL/s"))
        controls_layout.addLayout(self.make_slider_row("Fluid Velocity:", self.slider_velocity, self.val_vel))

        self.val_samp = QLabel(f"{int(self.sampling_rate * 100)} min")
        self.val_samp.setObjectName("ValueLabel")
        self.slider_sampling = QSlider(Qt.Horizontal)
        self.slider_sampling.setRange(0, 100)
        self.slider_sampling.setValue(int(self.sampling_rate * 100))
        self.slider_sampling.valueChanged.connect(lambda val: self.update_slider(self.val_samp, val, MessageID.M_RATE, " min"))
        controls_layout.addLayout(self.make_slider_row("Sampling Rate:", self.slider_sampling, self.val_samp))

        # Divider Line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #1F1F2E;")
        controls_layout.addWidget(line)

        # Checkboxes
        self.check_pumpdial = QCheckBox("Pump Dialysate Enable")
        self.check_pumpdye = QCheckBox("Pump Dye Enable")
        self.check_leduv = QCheckBox("LED UV Activate")
        self.check_ledblu = QCheckBox("LED Blue Activate")
        self.check_ledred = QCheckBox("LED Red Activate")
        
        self.check_pumpdial.stateChanged.connect(lambda state: self.request_send.emit(MessageID.M_PUMP_1, bool(state)))
        self.check_pumpdye.stateChanged.connect(lambda state: self.request_send.emit(MessageID.M_PUMP_2, bool(state)))
        self.check_leduv.stateChanged.connect(lambda state: self.request_send.emit(MessageID.M_LED_UV, bool(state)))
        self.check_ledblu.stateChanged.connect(lambda state: self.request_send.emit(MessageID.M_LED_BLU, bool(state)))
        self.check_ledred.stateChanged.connect(lambda state: self.request_send.emit(MessageID.M_LED_RED, bool(state)))

        controls_layout.addWidget(self.check_pumpdye)
        controls_layout.addWidget(self.check_pumpdial)
        controls_layout.addWidget(self.check_leduv)
        controls_layout.addWidget(self.check_ledblu)
        controls_layout.addWidget(self.check_ledred)
        controls_layout.addStretch()
        
        # Program Menu
        self.btn_program = QPushButton("▶ EXECUTE PROGRAM")
        self.program_menu = QMenu(self)
        self.program_menu.setToolTipsVisible(True)
        for state in ProgramState:
            info = STATE_INFO.get(state)
            if info:
                action = QWidgetAction(self.program_menu)
                item_btn = QPushButton(info["name"])
                item_btn.setToolTip(info["tooltip"])
                item_btn.setStyleSheet("""QPushButton {background-color: transparent; border: none; color: #00E5FF; padding: 10px 20px; font-weight: bold; text-align: left;} QPushButton:hover {background-color: #00E5FF; color: #0D0D12;}""")
                item_btn.clicked.connect(lambda checked=False, s=state: (self.program_menu.hide(), self.request_send.emit(MessageID.M_PROGRAM, s)))
                action.setDefaultWidget(item_btn)
                self.program_menu.addAction(action)
        self.btn_program.setMenu(self.program_menu)
        controls_layout.addWidget(self.btn_program)

        self.main_splitter.addWidget(controls_widget)


        # Right Panel: Graph
        pg.setConfigOptions(antialias=True)
        self.layout_2d = pg.GraphicsLayoutWidget()
        axis_pen = pg.mkPen(color='#A0A0B0', width=1)
        
        self.p1 = self.layout_2d.addPlot(row=0, col=0)
        self.p1.setLabel('left', 'Original', color='red')
        
        self.p2 = self.layout_2d.addPlot(row=1, col=0)
        self.p2.setLabel('left', 'Double', color='orange')
        
        self.p3 = self.layout_2d.addPlot(row=2, col=0)
        self.p3.setLabel('left', 'Triple', color='yellow')
        self.p3.setLabel('bottom', 'Time/Iteractions', color='#A0A0B0')

        # Limiting and styling axes
        for p in [self.p1, self.p2, self.p3]:
            p.getAxis('bottom').setPen(axis_pen)
            p.getAxis('left').setPen(axis_pen)
            p.setLimits(xMin=0)
        self.curve1 = self.p1.plot(pen=pg.mkPen('r', width=2))
        self.curve2 = self.p2.plot(pen=pg.mkPen((255, 150, 0), width=2))
        self.curve3 = self.p3.plot(pen=pg.mkPen('y', width=2))
        
        # Linking X axes
        self.p2.setXLink(self.p1)
        self.p3.setXLink(self.p1)

        # Vertical line for mouse tracking
        pen_mirino = pg.mkPen(color='#00E5FF', width=1, style=Qt.DashLine)
        self.vLine1 = pg.InfiniteLine(angle=90, movable=False, pen=pen_mirino)
        self.vLine2 = pg.InfiniteLine(angle=90, movable=False, pen=pen_mirino)
        self.vLine3 = pg.InfiniteLine(angle=90, movable=False, pen=pen_mirino)
        
        self.vLine1.setZValue(100)
        self.vLine2.setZValue(100)
        self.vLine3.setZValue(100)

        self.p1.addItem(self.vLine1, ignoreBounds=True)
        self.p2.addItem(self.vLine2, ignoreBounds=True)
        self.p3.addItem(self.vLine3, ignoreBounds=True)

        # Tooltips for data points
        self.tip1 = pg.TextItem(text="", color='#0D0D12', fill=pg.mkBrush('#00E5FF'))
        self.tip2 = pg.TextItem(text="", color='#0D0D12', fill=pg.mkBrush('#00E5FF'))
        self.tip3 = pg.TextItem(text="", color='#0D0D12', fill=pg.mkBrush('#00E5FF'))
        
        self.tip1.setZValue(100)
        self.tip2.setZValue(100)
        self.tip3.setZValue(100)

        self.p1.addItem(self.tip1, ignoreBounds=True)
        self.p2.addItem(self.tip2, ignoreBounds=True)
        self.p3.addItem(self.tip3, ignoreBounds=True)
        
        self.tip1.hide()
        self.tip2.hide()
        self.tip3.hide()
        
        # Mouse Interaction
        self.proxy = pg.SignalProxy(self.layout_2d.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_moved)
        self.layout_2d.scene().sigMouseClicked.connect(self.mouse_clicked)

        # Initialization of data
        self.show_tooltip = False
        self.x_index = 0
        self.data_x = []
        self.data_y1, self.data_y2, self.data_y3 = [], [], []

        self.main_splitter.addWidget(self.layout_2d)
        self.main_splitter.setSizes([300, 1100])

        # Thread
        self.thread = QThread()
        self.worker = SerialManager("/dev/cu.usbserial-110", 115200)
        self.worker.moveToThread(self.thread)
        self.request_send.connect(self.worker.send_package, Qt.DirectConnection)
        self.thread.started.connect(self.worker.start)
        self.worker.data_received.connect(self.update_graph_data)
        self.worker.ack_received.connect(self.handle_ack)
        self.worker.error_occurred.connect(self.handle_error)
        self.thread.start()

    def make_slider_row(self, title, slider, value_label):
        v_lay = QVBoxLayout()
        h_lay = QHBoxLayout()
        h_lay.addWidget(QLabel(title))
        h_lay.addStretch()
        h_lay.addWidget(value_label)
        v_lay.addLayout(h_lay)
        v_lay.addWidget(slider)
        return v_lay

    def update_slider(self, label, val, msg_id, suffix):
        label.setText(f"{val}{suffix}")
        if msg_id:
            self.request_send.emit(msg_id, val)
    
    def mouse_clicked(self, evt):
        if evt.button() == Qt.LeftButton:
            self.show_tooltip = not self.show_tooltip
            if not self.show_tooltip:
                self.tip1.hide()
                self.tip2.hide()
                self.tip3.hide()

    def mouse_moved(self, evt):
        pos = evt[0]

        # If mouse is within the plotting area, show vertical lines and tooltips
        if self.layout_2d.rect().contains(pos.toPoint()):
            mousePoint = self.p1.vb.mapSceneToView(pos)
            target_x = int(mousePoint.x())
            
            self.vLine1.setPos(target_x)
            self.vLine2.setPos(target_x)
            self.vLine3.setPos(target_x)

            if self.show_tooltip and target_x in self.data_x:
                list_idx = self.data_x.index(target_x)
                v1 = self.data_y1[list_idx]
                v2 = self.data_y2[list_idx]
                v3 = self.data_y3[list_idx]
                
                testo = f"Iter: {target_x}\nOrig: {v1:.1f}\nDouble: {v2:.1f}\nTripl: {v3:.1f}"

                self.tip1.hide()
                self.tip2.hide()
                self.tip3.hide()

                # Check which plot the mouse is over and show the corresponding tooltip
                if self.p1.vb.sceneBoundingRect().contains(pos):
                    self.tip1.setText(testo)
                    self.tip1.setPos(target_x, v1)
                    self.tip1.show()
                elif self.p2.vb.sceneBoundingRect().contains(pos):
                    self.tip2.setText(testo)
                    self.tip2.setPos(target_x, v2)
                    self.tip2.show()
                elif self.p3.vb.sceneBoundingRect().contains(pos):
                    self.tip3.setText(testo)
                    self.tip3.setPos(target_x, v3)
                    self.tip3.show()

    @Slot(str)
    def handle_error(self, error_message):
        QMessageBox.critical(self, "System Error", f"Detected Serial Error:\n{error_message}")

    @Slot(bool)
    def handle_ack(self, ack):
        pass

    @Slot(int, bytes)
    def update_graph_data(self, ID_message, data_bytes):
        try:
            pf = PAYLOAD_FORMATS[ID_message]
            valore = struct.unpack(pf, data_bytes)[0] if pf else 0
            if ID_message == MessageID.M_ABS_UV:
                V = valore
                v_orig = V
                v_doub = V * 2
                v_tripl = V * 3

                self.data_x.append(self.x_index)
                self.data_y1.append(v_orig)
                self.data_y2.append(v_doub)
                self.data_y3.append(v_tripl)

                if len(self.data_x) > 200:
                    self.data_x.pop(0)
                    self.data_y1.pop(0)
                    self.data_y2.pop(0)
                    self.data_y3.pop(0)

                self.curve1.setData(self.data_x, self.data_y1)
                self.curve2.setData(self.data_x, self.data_y2)
                self.curve3.setData(self.data_x, self.data_y3)

                self.x_index += 1
        except Exception as e:
            pass

    def closeEvent(self, event):
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)
    window = GUIManager()
    window.show()
    sys.exit(app.exec())