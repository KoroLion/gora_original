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


class ServerCore(object):
    """!
    @brief главный класс сервера
    Занимается обработкой комманд и хранением данных
    """
    def __init__(self, ip: str, port: int):
        self.players = {}
        self.terminated = False

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


async def tcp_handle(reader, writer):
    while True:
        data = await reader.read(2048)  # read(100) - читать 100 байт, иначе до EOF
        if not data:
            break

        addr = writer.get_extra_info('peername')

        data = data.decode()
        try:
            data = json.loads(data)
            correct_data = True
        except json:
            print('#ERROR: incorrect format of input data')
            correct_data = False

        if correct_data:
            command = data.get(J_COMMAND)
            token = data.get(J_TOKEN)
            players = server.players
            cur_player_token = token

            if data.get(J_COMMAND) == CONNECT:
                print(token + ' (' + addr[0] + ') connected!')
                new_player = {token: PlayerInfo(Point(100, 100), Point(0, 0),
                                                ip=addr[0],
                                                skin=data.get(J_SKIN),
                                                angle=data.get(J_ANGLE))
                              }
                players.update(new_player)
                writer.write('OK'.encode())
            elif command == GO_TOP:
                players[token].speed.x = 0
                players[token].speed.y = -players[token].speed_amount
                writer.write('OK'.encode())
            elif command == GO_BOTTOM:
                players[token].speed.x = 0
                players[token].speed.y = players[token].speed_amount
                writer.write('OK'.encode())
            elif command == GO_LEFT:
                players[token].speed.x = -players[token].speed_amount
                players[token].speed.y = 0
                writer.write('OK'.encode())
            elif command == GO_RIGHT:
                players[token].speed.x = players[token].speed_amount
                players[token].speed.y = 0
                writer.write('OK'.encode())
            elif command == GET_DATA:
                angle = round(data.get(J_ANGLE))

                server.players[cur_player_token].angle = angle
                j_players = []
                for token in server.players:
                    data = {J_TOKEN: token,
                            J_POSITION_X: server.players[token].position.x,
                            J_POSITION_Y: server.players[token].position.y,
                            J_ANGLE: server.players[token].angle,
                            J_SKIN: server.players[token].skin}
                    j_players.append(data)

                writer.write(json.dumps(j_players).encode())
            elif command == DISCONNECT:
                print(cur_player_token + ' (' + players[cur_player_token].ip + ') disconnected!')
                server.disconnect_player(cur_player_token)
                writer.write('OK'.encode())

    writer.close()

async def main():
    while not server.terminated:
        server.update_players()
        await asyncio.sleep(0.05)

if __name__ == "__main__":
    asyncio_loop = asyncio.get_event_loop()

    print('*GORA server pre-alpha 0.1*')
    print('Initializing server...')
    server = ServerCore(IP, PORT)

    print('Setting up TCP server...')
    coro = asyncio.start_server(tcp_handle, '', PORT, loop=asyncio_loop)
    print('Starting TCP server at {}:{}...'.format(IP, PORT))
    try:
        tcp_server = asyncio_loop.run_until_complete(coro)
    except OSError:
        print('Error while attempting to bind on address {}:{}'.format(IP, PORT))
        sys.exit()

    # сервер запущен, пока не нажали Ctrl+C
    addr = tcp_server.sockets[0].getsockname()
    print('TCP server started at {}:{}'.format(addr[0], addr[1]))

    asyncio_loop.run_until_complete(main())
    asyncio_loop.close()

    tcp_server.close()
