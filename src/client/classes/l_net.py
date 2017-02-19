import socket

PACKET_SIZE = 512


class LNet(object):
    """
    Класс для простой работы с сетью
    """
    def __init__(self, ip, port, timeout):
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def tcp_send(self, data):
        # IPv4, потокориентированный, TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
        sock.connect((self.ip, self.port))
        sock.sendall(data)
        data = sock.recv(PACKET_SIZE)
        sock.close()
        return data

    def udp_send(self, data):
        # IPv4, датаграммный, UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((self.ip, self.port))
        sock.sendall(data)
        sock.close()