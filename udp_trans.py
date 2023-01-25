"""
Listen to udp port and receive data packets consisting of float numbers
"""
import asyncio
import logging.config
import sys
import threading
import time

import numpy
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QMainWindow, QVBoxLayout

UDP_PORT = 61111

logger = logging.getLogger(__name__)


class Server(asyncio.DatagramProtocol, QThread):
    """
    UDP Server that listens on a given port and handles UDP Datagrams
    with arrays of floating point numbers.
    """

    dataReceived = pyqtSignal(object)

    def __init__(self, port: int):
        super().__init__()
        self.loop = asyncio.new_event_loop()
        self.port = port
        self.server = None
        self.transport = None
        self.start()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        logger.debug("received a datagram package")
        numbers = numpy.frombuffer(data)
        self.dataReceived.emit(numbers)

    def run(self):
        asyncio.set_event_loop(self.loop)
        print(f"creating datagram endpoint on port {self.port}")
        co_endp = self.loop.create_datagram_endpoint(lambda: self, local_addr=('127.0.0.1', self.port))
        self.transport, protocol = self.loop.run_until_complete(co_endp)
        print(f"datagram endpoint ready, switching to loop now")
        print(f"starting loop run_forever (thread: {threading.get_ident()})")
        self.loop.run_forever()
        self.transport.close()
        self.loop.close()
        print("Loop finished graceful")

    def stop(self):
        """Call loops stop method. Thread safe"""
        self.loop.call_soon_threadsafe(self.loop.stop)


class MainWindow(QMainWindow):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.btnExit = QPushButton("Exit")
        self.btnExit.clicked.connect(self.app.quit)
        self.layout.addWidget(self.btnExit)
        self.central_widget.setLayout(self.layout)
        self.app.aboutToQuit.connect(self.close)
        self.server = Server(UDP_PORT)
        self.server.dataReceived.connect(self.data_recieved)

    @pyqtSlot(object)
    def data_recieved(self, numbers):
        print(f"Numbers received: {numbers}")

    def close(self):
        self.server.stop()


def main():
    """
    Main function for terminal. Interrupt with Ctrl-C.
    """
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()

