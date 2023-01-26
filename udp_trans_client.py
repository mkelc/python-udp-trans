"""
Encode numpy arrays and send them via udp periodically
"""
import logging.config
import socket
import sys

import numpy
import numpy.random
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QThread, QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QPushButton, QWidget

from udp_trans import UDP_PORT

logger = logging.getLogger(__name__)


class DatagramThread(QObject):

    sig_cleanup = pyqtSignal()

    def __init__(self):
        super().__init__(None)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.sig_cleanup.connect(self.cleanup)
        self.thread.start()

    def close(self):
        self.sig_cleanup.emit()

    @pyqtSlot()
    def send_data(self):
        numbers = 600.0 * (numpy.random.random_sample((300,)) - 0.5)
        data = numbers.tobytes('C')
        self.socket.sendto(data, ('127.0.0.1', UDP_PORT))

    @pyqtSlot()
    def cleanup(self):
        print("Cleanin up dgram sender")
        self.socket.close()
        self.socket = None


class MainWindow(QMainWindow):

    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.setWindowTitle("Trans Client")
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.btnStart = QPushButton("Start Transmission")
        self.btnStop = QPushButton("Stop Transmission")
        self.btnExit = QPushButton("Exit")
        for _btn in (self.btnStart, self.btnStop, self.btnExit):
            self.layout.addWidget(_btn)
        self.central_widget.setLayout(self.layout)
        self.btnStart.clicked.connect(self.hstart)
        self.btnStop.clicked.connect(self.hstop)
        self.btnExit.clicked.connect(self.app.quit)
        self.setCentralWidget(self.central_widget)
        self.dgram = DatagramThread()
        self.timer = QTimer()
        self.timer.timeout.connect(self.dgram.send_data)
        self.app.aboutToQuit.connect(self.cleanup)

    def hstart(self):
        self.timer.start(10)

    def hstop(self):
        self.timer.stop()

    @pyqtSlot()
    def cleanup(self):
        print("Cleaning up main window")
        self.dgram.close()


def qt_main():
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec()


if __name__ == "__main__":
    qt_main()