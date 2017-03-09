import sys
import asyncio

try:
    import ujson as json
    print('using ujson...')
except ModuleNotFoundError:
    import json
    print('using json...')

from classes.helper_types import Point
from classes.network_constants import *

IP = '0.0.0.0'

DIR_LEFT = 1
DIR_RIGHT = 2
DIR_TOP = 3
DIR_BOTTOM = 4


class ServerCore(object):
    """!
    @brief главный класс сервера
    Занимается обработкой комманд и хранением данных
    """
    def __init__(self, ip: str, port: int):
        self.new_pid = 0
        self.players = {}
        self.terminated = False

    def get_new_pid(self):
        self.new_pid += 1
        return self.new_pid

    def start_server(self):
        pass

    def disconnect_player(self, token: str) -> bool:  # todo: обработка ошибок
        self.players[token].position = Point(1, 1)
        self.players[token].speed = Point(0, 0)
        self.players.pop(token)
        return True

    def terminate(self):
        self.terminated = True

    def update_players(self):
        for player in self.players:
            self.players[player].update()


class PlayerInfo:
    """!
    @brief Класс информации об игроке, хранящейся на сервере
    """
    def __init__(self, pid, position: Point, speed: Point, angle: int=50, ip: str='', skin: int=0, login: str=''):
        self.id = pid
        self.position = position
        self.angle = angle
        self.speed = speed
        self.ip = ip
        self.speed_amount = 5
        self.login = login
        self.skin = skin

        # для игнорирования отпускания кнопки после нажатия противоположной ей
        # чтобы игрок не остановился после отпускания D, если была нажата A
        self.ignore_command = {C_GO_TOP_UP: False, C_GO_BOTTOM_DOWN: False, C_GO_LEFT_UP: False, C_GO_RIGHT_UP: False}

    def update(self):
        self.position.x += self.speed.x
        self.position.y += self.speed.y

async def game(transport: asyncio.transports):
    while not server.terminated:
        server.update_players()

        j_players = []
        for addr in server.players:
            data = {J_ID: server.players[addr].id,
                    J_POSITION_X: server.players[addr].position.x,
                    J_POSITION_Y: server.players[addr].position.y,
                    J_ANGLE: server.players[addr].angle,
                    J_SKIN: server.players[addr].skin}
            j_players.append(data)

        for addr in server.players:
            transport.sendto((json.dumps([DATA, j_players])).encode(), addr)

        await asyncio.sleep(0.05)


class EchoServerProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        print('Disconnected!')

    def datagram_received(self, data, addr):
        data = data.decode()

        try:
            data = json.loads(data)
            correct_data = True
        except json:
            print('#ERROR: incorrect format of input data')
            correct_data = False

        if correct_data:
            command = data[0]
            players = server.players
            player = server.players.get(addr)

            # подключение, отключение и передача данных
            if command == CONNECT:
                pid = server.get_new_pid()
                print('{} connected ({}:{})!'.format(data[1], addr[0], addr[1]))
                new_player = {addr: PlayerInfo(pid, Point(100, 100), Point(0, 0),
                                                login=data[1],
                                                skin=data[2],
                                                angle=0)
                              }
                players.update(new_player)

                data = json.dumps([ID, pid])
                self.transport.sendto(data.encode(), addr)
            elif command == DISCONNECT:
                login = server.players[addr].login
                print('{} disconnected ({}:{})!'.format(login, addr[0], addr[1]))
                server.disconnect_player(addr)
            elif command == BUTTON_DOWN:
                button = data[1]
                if button == B_GO_TOP:
                    player.ignore_command[B_GO_TOP] = False
                    player.ignore_command[B_GO_BOTTOM] = True
                    player.speed.y = -player.speed_amount
                elif button == B_GO_BOTTOM:
                    player.ignore_command[B_GO_TOP] = True
                    player.ignore_command[B_GO_BOTTOM] = False
                    player.speed.y = player.speed_amount
                elif button == B_GO_LEFT:
                    player.ignore_command[B_GO_LEFT] = False
                    player.ignore_command[B_GO_RIGHT] = True
                    player.speed.x = -player.speed_amount
                elif button == B_GO_RIGHT:
                    player.ignore_command[B_GO_LEFT] = True
                    player.ignore_command[B_GO_RIGHT] = False
                    player.speed.x = player.speed_amount
            elif command == BUTTON_UP:
                button = data[1]
                if button == B_GO_TOP and not player.ignore_command[B_GO_TOP] or \
                        button == B_GO_BOTTOM and not player.ignore_command[B_GO_BOTTOM]:
                    player.speed.y = 0
                elif button == B_GO_LEFT and not player.ignore_command[B_GO_LEFT] or \
                        button == B_GO_RIGHT and not player.ignore_command[B_GO_RIGHT]:
                    player.speed.x = 0
            elif command == ANGLE:
                new_angle = data[1]
                player = server.players[addr]
                player.angle = new_angle

            # обработка нажатий клавиш
            elif command == C_GO_TOP_DOWN:
                player.ignore_command[C_GO_TOP_UP] = False
                player.ignore_command[C_GO_BOTTOM_UP] = True
                player.speed.y = -player.speed_amount
            elif command == C_GO_BOTTOM_DOWN:
                player.ignore_command[C_GO_TOP_UP] = True
                player.ignore_command[C_GO_BOTTOM_UP] = False
                player.speed.y = player.speed_amount
            elif command == C_GO_LEFT_DOWN:
                player.ignore_command[C_GO_RIGHT_UP] = True
                player.ignore_command[C_GO_LEFT_UP] = False
                player.speed.x = -player.speed_amount
            elif command == C_GO_RIGHT_DOWN:
                player.ignore_command[C_GO_RIGHT_UP] = False
                player.ignore_command[C_GO_LEFT_UP] = True
                player.speed.x = player.speed_amount

            # обработка отпускания клавиш
            elif command == C_GO_TOP_UP and not player.ignore_command[C_GO_TOP_UP]:
                player.speed.y = 0
            elif command == C_GO_BOTTOM_UP and not player.ignore_command[C_GO_BOTTOM_UP]:
                player.speed.y = 0
            elif command == C_GO_LEFT_UP and not player.ignore_command[C_GO_LEFT_UP]:
                player.speed.x = 0
            elif command == C_GO_RIGHT_UP and not player.ignore_command[C_GO_RIGHT_UP]:
                player.speed.x = 0


if __name__ == "__main__":
    asyncio_loop = asyncio.get_event_loop()

    print('*GORA server pre-alpha 0.1*')
    print('Initializing server...')
    server = ServerCore(IP, PORT)

    print('Starting up UDP server...')
    # One protocol instance will be created to serve all client requests
    listen = asyncio_loop.create_datagram_endpoint(
        EchoServerProtocol, local_addr=(IP, PORT))
    transport, protocol = asyncio_loop.run_until_complete(listen)

    asyncio_loop.run_until_complete(game(transport))

    transport.close()
    asyncio_loop.close()
