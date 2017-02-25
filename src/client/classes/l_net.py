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
        self.loop = None

    def tcp_send(self, data: str) -> str:
        # IPv4, потокориентированный, TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
        sock.connect((self.ip, self.port))
        sock.sendall(data.encode())
        data = sock.recv(PACKET_SIZE)
        sock.close()
        return data

    def tcp_send_async(self, data: str, loop) -> str:
        @asyncio.coroutine
        def tcp_echo_client(message, loop):
            reader, writer = yield from asyncio.open_connection(self.ip, self.port, loop=loop)

            writer.write(message.encode())
            writer.write_eof()

            recv = yield from reader.read()
            writer.close()

            return recv.decode()

        data = loop.run_until_complete(tcp_echo_client(data, loop))
        loop.close()
        return data

    def udp_send(self, data: str) -> str:
        # IPv4, датаграммный, UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((self.ip, self.port))
        sock.sendall(data.encode())
        data = sock.recv(PACKET_SIZE)
        sock.close()
        return data.decode()
