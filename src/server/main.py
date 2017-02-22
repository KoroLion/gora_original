# -*- coding: utf-8 -*-

import socketserver
import threading
from time import sleep
import json

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

# constants for JSON
J_COMMAND = '1'
J_TOKEN = '2'
J_LOGIN = '3'
J_POSITION_X = '10'
J_POSITION_Y = '11'


class PlayerInfo:
    """!
    Класс информации об игроке, хранящейся на сервере
    """
    def __init__(self, position, speed, ip=''):
        self.position = position
        self.speed = speed
        self.ip = ip
        self.speed_amount = 3
        self.color = 0

    def update(self):
        self.position.x += self.speed.x
        self.position.y += self.speed.y

players = {}


class TCPHandler(socketserver.BaseRequestHandler):
    """!
    @brief поток обработчика TCP запросов
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        data = self.request.recv(PACKET_SIZE)

        if data:
            data = data.decode()
            data = json.loads(data)
            cur_thread = threading.current_thread()
            # print("{} wrote: {}".format(self.client_address[0], data))

            if data.get(J_COMMAND) == GET_DATA:
                j_players = []
                for token in players:
                    data = {J_TOKEN: token, J_POSITION_X: players[token].position.x, J_POSITION_Y: players[token].position.y}
                    j_players.append(data)
                self.request.sendall(json.dumps(j_players).encode())
            elif data.get(J_COMMAND) == CONNECT:
                print(data[J_TOKEN] + ' (' + self.client_address[0] + ') connected!')
                new_player = {data[J_TOKEN]: PlayerInfo(Position(1, 1), Position(0, 0), self.client_address[0])}
                players.update(new_player)


class UDPHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        cur_thread = threading.current_thread()
        # self.request это TCP сокет подключённый к клиенту
        data = self.request[0]
        if data:
            data = data.decode()
            try:
                data = json.loads(data)
                correct_data = True
            except json.decoder.JSONDecodeError:
                print('#ERROR: incorrect format of input data')
                correct_data = False

            if correct_data:
                command = data.get(J_COMMAND)
                token = data.get(J_TOKEN)
                if command == GO_TOP:
                    players[token].speed.x = 0
                    players[token].speed.y = -players[token].speed_amount
                elif command == GO_BOTTOM:
                    players[token].speed.x = 0
                    players[token].speed.y = players[token].speed_amount
                elif command == GO_LEFT:
                    players[token].speed.x = -players[token].speed_amount
                    players[token].speed.y = 0
                elif command == GO_RIGHT:
                    players[token].speed.x = players[token].speed_amount
                    players[token].speed.y = 0
                elif command == DISCONNECT:
                    players[token].position = Position(1, 1)
                    players[token].speed = Position(0, 0)
                    print(token + ' (' + players[token].ip + ') disconnected!')
                    players.pop(token)

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
