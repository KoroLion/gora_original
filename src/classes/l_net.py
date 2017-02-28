import socket
import asyncio
from time import sleep

PACKET_SIZE = 512


class LNet(object):
    """!
    @brief Класс для простой работы с сетью
    """
    def __init__(self, ip: str, port: int, timeout: float=0.5):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.loop = asyncio.new_event_loop()
        self.connected = False

        async def tcp_init(loop):
            reader, writer = await asyncio.open_connection(self.ip, self.port, loop=loop)
            return reader, writer

        try:
            self.reader, self.writer = self.loop.run_until_complete(tcp_init(self.loop))
            self.connected = True
        except ConnectionError:
            print('Connection error!')

    def tcp_send(self, data: str) -> str:
        if self.connected:
            async def tcp_echo_client(message):
                message += '\n'
                self.writer.write(message.encode())

                recv = await self.reader.read(1024)

                return recv.decode()

            data = self.loop.run_until_complete(tcp_echo_client(data))
            return data

    def disconnect(self):
        self.writer.close()
        self.connected = False
