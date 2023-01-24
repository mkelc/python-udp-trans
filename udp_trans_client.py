"""
Encode numpy arrays and send them via udp periodically
"""
import asyncio
import logging.config
import sys

import numpy
import numpy.random

from udp_trans import UDP_PORT

logger = logging.getLogger(__name__)


class TransClient(asyncio.DatagramProtocol):

    @classmethod
    async def connect(cls, port: int = UDP_PORT):
        client = TransClient()
        loop = asyncio.get_running_loop()
        await loop.create_datagram_endpoint(lambda: client, remote_addr=('127.0.0.1', port))
        return client

    def __init__(self, port: int = UDP_PORT):
        super().__init__()
        self.port = port
        self.transport = None

    def close(self):
        self.transport.close()

    def connection_made(self, transport):
        self.transport = transport

    async def co_send_data(self, data):
        self.transport.sendto(data)

    def datagram_received(self, datagram, addr):
        pass


async def co_period_send_data():
    udp_client = await TransClient.connect(UDP_PORT)
    while True:
        numbers = 600.0 * (numpy.random.random_sample((4,))-0.5)
        data = numbers.tobytes('C')
        await udp_client.co_send_data(data)
        await asyncio.sleep(0.01) # sleep for 10 ms


def main():
    asyncio.run(co_period_send_data())


if __name__ == "__main__":
    main()