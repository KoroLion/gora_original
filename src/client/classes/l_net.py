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

        async def tcp_init(loop):
            reader, writer = await asyncio.open_connection(self.ip, self.port, loop=loop)
            return reader, writer

        self.reader, self.writer = self.loop.run_until_complete(tcp_init(self.loop))

    def tcp_send_socket(self, data: str) -> str:
        # IPv4, потокориентированный, TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
        sock.connect((self.ip, self.port))
        sock.sendall(data.encode())
        data = sock.recv(PACKET_SIZE)
        sock.close()
        return data

    def tcp_send(self, data: str) -> str:
        async def tcp_echo_client(message):
            self.writer.write(message.encode())

            recv = await self.reader.read(1024)

            return recv.decode()

        data = self.loop.run_until_complete(tcp_echo_client(data))
        return data

    def udp_send(self, data: str) -> str:
        # IPv4, датаграммный, UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((self.ip, self.port))
        sock.sendall(data.encode())
        data = sock.recv(PACKET_SIZE)
        sock.close()
        return data.decode()
