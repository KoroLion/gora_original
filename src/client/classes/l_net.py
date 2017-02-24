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

    def tcp_send_old(self, data: str) -> str:
        # IPv4, потокориентированный, TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
        sock.connect((self.ip, self.port))
        sock.sendall(data.encode())
        data = sock.recv(PACKET_SIZE)
        sock.close()
        return data

    def tcp_send(self, data: str) -> str:
        self.loop = asyncio.get_event_loop()
        while self.loop.is_closed():
            pass

        @asyncio.coroutine
        def tcp_echo_client(message, loop):
            reader, writer = yield from asyncio.open_connection(self.ip, self.port, loop=loop)

            writer.write(message.encode())
            writer.write_eof()

            recv = yield from reader.read()
            writer.close()

            return recv.decode()

        data = self.loop.run_until_complete(tcp_echo_client(data, self.loop))
        self.loop.close()
        return data

    def udp_send(self, data: str) -> str:
        self.loop = asyncio.get_event_loop()
        while self.loop.is_closed():
            pass

        class EchoClientProtocol(asyncio.DatagramProtocol):
            def __init__(self, message, loop):
                self.message = message
                self.loop = loop
                self.transport = None
                self.received = ''

            def connection_made(self, transport):
                self.transport = transport
                self.transport.sendto(self.message.encode())

            def datagram_received(self, data, addr):
                self.received = data.decode()
                self.transport.close()

            def error_received(self, exc):
                print('Error received:', exc)

            def connection_lost(self, exc):
                self.loop.stop()

        connect = self.loop.create_datagram_endpoint(
            lambda: EchoClientProtocol(data, self.loop),
            remote_addr=(self.ip, self.port))
        transport, protocol = self.loop.run_until_complete(connect)
        self.loop.run_forever()
        transport.close()
        self.loop.close()
        return protocol.received

    def udp_send_(self, data: str) -> str:
        # IPv4, датаграммный, UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((self.ip, self.port))
        sock.sendall(data.encode())
        data = sock.recv(PACKET_SIZE)
        sock.close()
        return data.decode()
