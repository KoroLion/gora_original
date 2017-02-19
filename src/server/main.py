# -*- coding: utf-8 -*-

import socketserver
import threading
from time import sleep
import pickle

from classes.helper_types import Position

PORT = 22000
PACKET_SIZE = 512

GO_LEFT = 1
GO_RIGHT = 2
GO_TOP = 3
GO_BOTTOM = 4

CONNECT = 5
GET_DATA = 6
DISCONNECT = 7


class PlayerInfo:
    """
    Класс информации об игроке, хранящейся на сервере
    """
    def __init__(self, position, speed):
        self.position = position
        self.speed = speed
        self.speed_amount = 3

    def update(self):
        self.position.x += self.speed.x
        self.position.y += self.speed.y

players = {}
#new_player = {'korolion': PlayerInfo(Position(1, 1), Position(0, 0))}
#players.update(new_player)


class TCPHandler(socketserver.BaseRequestHandler):
    """
    Запускаем
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        data = self.request.recv(PACKET_SIZE)

        if data:
            data = data.decode()
            data = data.split()
            data[0] = int(data[0])
            cur_thread = threading.current_thread()
            # print("{} wrote: {}".format(self.client_address[0], data))

            if data[0] == GET_DATA:
                self.request.sendall(pickle.dumps(players, 2))
            elif data[0] == CONNECT:
                print(data[1] + ' connected!')
                new_player = {data[1]: PlayerInfo(Position(1, 1), Position(0, 0))}
                players.update(new_player)


class UDPHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        data = self.request[0]
        if data:
            data = self.request[0].decode()
            data = data.split()
            data[0] = int(data[0])
            token = data[1]
            cur_thread = threading.current_thread()
            # print("{} wrote: {}".format(self.client_address[0], data))

            if data[0] == GO_TOP:
                players[token].speed.x = 0
                players[token].speed.y = -players[token].speed_amount
            elif data[0] == GO_BOTTOM:
                players[token].speed.x = 0
                players[token].speed.y = players[token].speed_amount
            elif data[0] == GO_LEFT:
                players[token].speed.x = -players[token].speed_amount
                players[token].speed.y = 0
            elif data[0] == GO_RIGHT:
                players[token].speed.x = players[token].speed_amount
                players[token].speed.y = 0
            elif data[0] == DISCONNECT:
                players[token].position = Position(1, 1)
                players[token].speed = Position(0, 0)
                players.pop(token)
                print(data[1] + ' disconnected!')

print('*GORA server pre-alpha 0.1*')
print('Initializing network...')
server = socketserver.ThreadingTCPServer(('', PORT), TCPHandler)

ip, port = server.server_address
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()

server_udp = socketserver.ThreadingUDPServer(('', PORT), UDPHandler)
server_udp_thread = threading.Thread(target=server_udp.serve_forever)
server_udp_thread.daemon = True
server_udp_thread.start()


def main():
    print('Server started at {}:{}!'.format(ip, port))
    while True:
        sleep(0.05)
        for player in players:
            players[player].update()

    server.shutdown()
    server.server_close()

if __name__ == "__main__":
    main()
