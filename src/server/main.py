# -*- coding: utf-8 -*-

import socketserver
import threading
from time import sleep
import json

from classes.helper_types import Point
from src.shared_constants import *

IP = ''


class ServerCore(object):
    """!
    @brief главный класс сервера
    Занимается обработкой комманд и хранением данных
    """
    def __init__(self, ip: str, port: int):
        self.server_tcp = socketserver.ThreadingTCPServer((ip, port), TCPHandler)
        self.server_udp = socketserver.ThreadingUDPServer((ip, port), UDPHandler)

        self.ip, self.port = self.server_tcp.server_address
        self.players = {}
        self.terminated = False

    def start_server(self):
        server_tcp_thread = threading.Thread(target=self.server_tcp.serve_forever)
        server_tcp_thread.daemon = True
        server_tcp_thread.start()

        server_udp_thread = threading.Thread(target=self.server_udp.serve_forever)
        server_udp_thread.daemon = True
        server_udp_thread.start()

    def terminate(self):
        self.server_tcp.shutdown()
        self.server_tcp.server_close()
        self.terminated = True

    def update_players(self):
        for player in self.players:
            self.players[player].update()


class PlayerInfo:
    """!
    @brief Класс информации об игроке, хранящейся на сервере
    """
    def __init__(self, position: Point, speed: Point, ip: str=''):
        self.position = position
        self.speed = speed
        self.ip = ip
        self.speed_amount = 3
        self.color = 0

    def update(self):
        self.position.x += self.speed.x
        self.position.y += self.speed.y


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
                for token in server.players:
                    data = {J_TOKEN: token,
                            J_POSITION_X: server.players[token].position.x,
                            J_POSITION_Y: server.players[token].position.y}
                    j_players.append(data)
                self.request.sendall(json.dumps(j_players).encode())
            elif data.get(J_COMMAND) == CONNECT:
                print(data[J_TOKEN] + ' (' + self.client_address[0] + ') connected!')
                new_player = {data[J_TOKEN]: PlayerInfo(Point(1, 1), Point(0, 0), self.client_address[0])}
                server.players.update(new_player)


class UDPHandler(socketserver.DatagramRequestHandler):
    """!
    @brief поток обработчика UDP запросов
    """

    def handle(self):
        players = server.players
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
                    players[token].position = Point(1, 1)
                    players[token].speed = Point(0, 0)
                    print(token + ' (' + players[token].ip + ') disconnected!')
                    players.pop(token)

print('*GORA server pre-alpha 0.1*')
print('Initializing server...')
server = ServerCore(IP, PORT)


def main():
    print('Starting server at {}:{}...'.format(server.ip, server.port))
    server.start_server()
    print('Server started at {}:{}!'.format(server.ip, server.port))
    while not server.terminated:
        sleep(0.05)
        server.update_players()

if __name__ == "__main__":
    main()
