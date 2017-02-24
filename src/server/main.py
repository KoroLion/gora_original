import socketserver
import asyncio
import threading
from time import sleep
import ujson as json

from src.helper_types import Point
from src.shared_constants import *

IP = ''


class ServerCore(object):
    """!
    @brief главный класс сервера
    Занимается обработкой комманд и хранением данных
    """
    def __init__(self, ip: str, port: int):
        # self.server_tcp = socketserver.ThreadingTCPServer((ip, port), TCPHandler)
        self.server_udp = socketserver.ThreadingUDPServer((ip, port), UDPHandler)

        self.ip, self.port = self.server_udp.server_address
        self.players = {}
        self.terminated = False

    def start_server(self):
        # server_tcp_thread = threading.Thread(target=self.server_tcp.serve_forever)
        # server_tcp_thread.daemon = True
        # server_tcp_thread.start()

        server_udp_thread = threading.Thread(target=self.server_udp.serve_forever)
        server_udp_thread.daemon = True
        server_udp_thread.start()

    def disconnect_player(self, token: str) -> bool:  # todo: обработка ошибок
        self.players[token].position = Point(1, 1)
        self.players[token].speed = Point(0, 0)
        self.players.pop(token)
        return True

    def terminate(self):
        # self.server_tcp.shutdown()
        # self.server_tcp.server_close()
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


@asyncio.coroutine
def tcp_handle(reader, writer):
    data = yield from reader.read()  # read(100) - читать 100 байт, иначе до EOF
    addr = writer.get_extra_info('peername')
    if data:
        data = data.decode()
        data = json.loads(data)
        command = data.get(J_COMMAND)
        token = data.get(J_TOKEN)
        players = server.players

        if data.get(J_COMMAND) == CONNECT:
            print(token + ' (' + addr[0] + ') connected!')
            new_player = {token: PlayerInfo(Point(1, 1), Point(0, 0),
                                            ip=addr[0],
                                            skin=data.get(J_SKIN),
                                            angle=data.get(J_ANGLE))
                          }
            players.update(new_player)
            writer.write('OK'.encode())
            writer.write_eof()
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

    writer.close()

    # data = data.decode()
    # writer.write(data.encode())
    # writer.close()


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

    main_thread = threading.Thread(target=main)
    main_thread.start()

    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(tcp_handle, '', PORT, loop=loop)
    tcp_server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(tcp_server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    tcp_server.close()
    loop.run_until_complete(tcp_server.wait_closed())
    loop.close()

    main()
