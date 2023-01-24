"""
Listen to udp port and receive data packets consisting of float numbers
"""
import asyncio
import logging.config
import threading

import numpy

UDP_PORT = 61111

logger = logging.getLogger(__name__)


class Server(asyncio.DatagramProtocol):
    """
    UDP Server that listens on a given port and handles UDP Datagrams
    with arrays of floating point numbers.
    """
    def __init__(self, port: int):
        super().__init__()
        self.loop = asyncio.get_event_loop()
        self.port = port
        self.server = None
        self.transport = None

        self.init_fut = self.loop.create_future()
        logger.info("udp server initialized")

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        logger.debug("received a datagram package")
        numbers = numpy.frombuffer(data)
        print("Data received:")
        print(numbers)

    def run(self):
        logger.info(f"creating datagram endpoint on port {self.port}")
        co_endp = self.loop.create_datagram_endpoint(lambda: self, local_addr=('127.0.0.1', self.port))
        self.transport, protocol = self.loop.run_until_complete(co_endp)
        logger.info(f"datagram endpoint ready, switching to loop now")
        logger.info(f"starting loop run_forever (thread: {threading.get_ident()})")
        self.loop.run_forever()
        self.transport.close()
        self.loop.close()

    def stop(self):
        """Call loops stop method. Thread safe"""
        self.loop.call_soon_threadsafe(self.loop.stop)


def main():
    """
    Main function for terminal. Interrupt with Ctrl-C.
    """
    mth = Server(UDP_PORT)
    logger.debug("Entering mother run now")
    mth.run()


if __name__ == "__main__":
    main()

