import socketserver
import threading
from time import sleep
import json

from src.helper_types import Point
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

    def disconnect_player(self, token: str) -> bool:  # todo: обработка ошибок
        self.players[token].position = Point(1, 1)
        self.players[token].speed = Point(0, 0)
        self.players.pop(token)
        return True

    def terminate(self):
        self.server_tcp.shutdown()
        self.server_tcp.server_close()
        self.server_udp.shutdown()
        self.server_udp.server_close()

        self.terminated = True

    def update_players(self):
        for player in self.players:
            self.players[player].update()


class PlayerInfo:
    """!
    @brief Класс информации об игроке, хранящейся на сервере
    """
    def __init__(self, position: Point, speed: Point, angle: int=50, ip: str='', skin: int=0):
        self.position = position
        self.angle = angle
        self.speed = speed
        self.ip = ip
        self.speed_amount = 3
        self.skin = skin

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
            command = data.get(J_COMMAND)
            token = data.get(J_TOKEN)
            players = server.players

            if data.get(J_COMMAND) == CONNECT:
                print(token + ' (' + self.client_address[0] + ') connected!')
                new_player = {token: PlayerInfo(Point(1, 1), Point(0, 0),
                                                ip=self.client_address[0],
                                                skin=data.get(J_SKIN),
                                                angle=data.get(J_ANGLE))
                              }
                players.update(new_player)
            elif command == GO_TOP:
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
                cur_player_token = data.get(J_TOKEN)
                if command == GET_DATA:
                    angle = data.get(J_ANGLE)

                    server.players[cur_player_token].angle = angle
                    j_players = []
                    for token in server.players:
                        data = {J_TOKEN: token,
                                J_POSITION_X: server.players[token].position.x,
                                J_POSITION_Y: server.players[token].position.y,
                                J_ANGLE: server.players[token].angle,
                                J_SKIN: server.players[token].skin}
                        j_players.append(data)

                    self.request[1].sendto(json.dumps(j_players).encode(), self.client_address)
                elif command == DISCONNECT:
                    print(cur_player_token + ' (' + players[cur_player_token].ip + ') disconnected!')
                    server.disconnect_player(cur_player_token)


def main():
    print('Starting server at {}:{}...'.format(server.ip, server.port))
    server.start_server()
    print('Server started at {}:{}!'.format(server.ip, server.port))
    while not server.terminated:
        sleep(0.05)
        server.update_players()

if __name__ == "__main__":
    print('*GORA server pre-alpha 0.1*')
    print('Initializing server...')
    server = ServerCore(IP, PORT)

    main()
