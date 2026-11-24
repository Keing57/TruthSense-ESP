import sys
import json
import serial
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPalette, QColor
import pyqtgraph as pg

class SerialThread(QThread):
    data_received = pyqtSignal(dict)

    def __init__(self, port="COM3", baudrate=115200):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = False
        self.serial_conn = None

    def run(self):
        self.running = True
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            while self.running:
                if self.serial_conn and self.serial_conn.is_open:
                    line = self.serial_conn.readline().decode("utf-8", errors="ignore").strip()
                    if line:
                        try:
                            data = json.loads(line)
                            if isinstance(data, dict):
                                self.data_received.emit(data)
                        except json.JSONDecodeError:
                            pass
        except Exception:
            pass
        finally:
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()

    def stop(self):
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.wait()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TruthSense Polygraph")
        self.resize(1000, 600)
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.sidebar_widget = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        self.sidebar_layout.setAlignment(Qt.AlignTop)
        self.sidebar_widget.setFixedWidth(220)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("#121212")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.addLegend()

        main_layout.addWidget(self.sidebar_widget)
        main_layout.addWidget(self.plot_widget, stretch=1)

        self.max_points = 200
        self.data_filtered = [0] * self.max_points
        self.data_baseline = [0] * self.max_points
        self.current_baseline = 0

        pen_filtered = pg.mkPen(color=(0, 255, 100), width=3)
        pen_baseline = pg.mkPen(color=(255, 215, 0), width=2, style=Qt.DashLine)

        self.curve_filtered = self.plot_widget.plot(self.data_filtered, pen=pen_filtered, name="Filtered")
        self.curve_baseline = self.plot_widget.plot(self.data_baseline, pen=pen_baseline, name="Baseline")

        self.serial_thread = SerialThread()
        self.serial_thread.data_received.connect(self.handle_data)
        self.serial_thread.start()

    def handle_data(self, data):
        filtered_val = data.get("filtered", data.get("raw", 0))
        baseline_val = data.get("baseline", self.current_baseline)
        self.current_baseline = baseline_val

        self.data_filtered.append(filtered_val)
        if len(self.data_filtered) > self.max_points:
            self.data_filtered.pop(0)

        self.data_baseline.append(baseline_val)
        if len(self.data_baseline) > self.max_points:
            self.data_baseline.pop(0)

        self.curve_filtered.setData(self.data_filtered)
        self.curve_baseline.setData(self.data_baseline)

    def closeEvent(self, event):
        if self.serial_thread and self.serial_thread.isRunning():
            self.serial_thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(35, 35, 35))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(35, 35, 35))
    palette.setColor(QPalette.ButtonText, Qt.white)
    app.setPalette(palette)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
