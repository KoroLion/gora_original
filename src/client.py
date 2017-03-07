"""!
@file Клиент
@brief Главный файл клиента
"""

import pygame
import math
import asyncio

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from classes.network_constants import *
from classes.helper_types import Size, Point
from classes.constants import FORM_WIDTH, FORM_HEIGHT, FPS

from classes.resources import Resources
from classes.core import Core
from classes.game import Game
from classes.game_object import Robot

IP = '127.0.0.1'
LOGIN = 'KoroLion'
SKIN = SKIN_BLUE
TRACKING_CAMERA = True

CENTER_POS = Point(FORM_WIDTH / 2, FORM_HEIGHT / 2)


class Client(object):
    """!
    @brief Храним данные для взаимодействия потоков и базовые команды клиента
    """

    def __init__(self):
        self.commands = []
        self.angle = 0
        self.id = None

    def connect(self):
        pass

    def send_commands(self):
        pass

    def disconnect(self):
        pass


def get_angle(pl_pos: Point, size: Size, m_pos: Point) -> float:
    """!
    @brief Возращает угол между мышью и объектом

    @param pl_pos: Point(координаты игрока)
    @param size: Size(helper_types)
    @param m_pos: Point(координаты мыши)
    @return: float(градус поворота)
    """
    x = pl_pos.x + size.width / 2 - m_pos.x
    y = pl_pos.y + size.height / 2 - m_pos.y
    if x == 0:
        if y >= 0:
            return 90
        else:
            return 270
    else:
        angle = math.degrees(math.atan(y / x))
        if x > 0:
            return 180 - angle
        else:
            return -angle

async def main(transport):
    """!
    @brief Поток отображения клиента
    """

    while not main_form.terminated:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main_form.terminate()
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    main_form.terminate()

                if event.key == pygame.K_w:
                    transport.sendto(json.dumps([BUTTON_DOWN, B_GO_TOP]).encode())
                    client.commands.append(C_GO_TOP_DOWN)
                if event.key == pygame.K_s:
                    transport.sendto(json.dumps([BUTTON_DOWN, B_GO_BOTTOM]).encode())
                    client.commands.append(C_GO_BOTTOM_DOWN)
                if event.key == pygame.K_a:
                    transport.sendto(json.dumps([BUTTON_DOWN, B_GO_LEFT]).encode())
                    client.commands.append(C_GO_LEFT_DOWN)
                if event.key == pygame.K_d:
                    transport.sendto(json.dumps([BUTTON_DOWN, B_GO_RIGHT]).encode())
                    client.commands.append(C_GO_RIGHT_DOWN)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    transport.sendto(json.dumps([BUTTON_UP, B_GO_TOP]).encode())
                    client.commands.append(C_GO_TOP_UP)
                if event.key == pygame.K_s:
                    transport.sendto(json.dumps([BUTTON_UP, B_GO_BOTTOM]).encode())
                    client.commands.append(C_GO_BOTTOM_UP)
                if event.key == pygame.K_a:
                    transport.sendto(json.dumps([BUTTON_UP, B_GO_LEFT]).encode())
                    client.commands.append(C_GO_LEFT_UP)
                if event.key == pygame.K_d:
                    transport.sendto(json.dumps([BUTTON_UP, B_GO_RIGHT]).encode())
                    client.commands.append(C_GO_RIGHT_UP)
            elif event.type == pygame.MOUSEMOTION:
                transport.sendto(json.dumps([ANGLE, client.angle]).encode())

        if game.players.get(client.id):
            # получаем объект игрока (который играет с этого клиента =) )
            player = game.players.get(client.id)

            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = Point(mouse_pos[0], mouse_pos[1])

            if TRACKING_CAMERA:
                client.angle = get_angle(CENTER_POS, player.size, mouse_pos)
            else:
                client.angle = get_angle(player.position, player.size, mouse_pos)

            res.update()
            game.update()
            main_form.update(camera_mode=TRACKING_CAMERA, point=player.position)

        await asyncio.sleep(0.01)

    data = json.dumps([DISCONNECT])
    transport.sendto(data.encode())


class EchoClientProtocol(asyncio.DatagramProtocol):
    def __init__(self, loop):
        self.loop = loop
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        data = json.dumps([CONNECT, SKIN])
        self.transport.sendto(data.encode())

    def datagram_received(self, data, addr):
        data = data.decode()
        data = json.loads(data)
        command = data[0]

        if command == DATA:
            players = data[1]

            # собираем ID сервера
            visible_pids = []
            for player in players:
                visible_pids.append(player[J_ID])

            # собираем ID клиента
            client_pids = []
            for pid in game.players:
                client_pids.append(pid)

            # удаляем лишние объекты игроков на клиенте (которые отключились)
            for pid in client_pids:
                if not pid in visible_pids:
                    game.players.pop(pid)

            for player in players:
                pid = player[J_ID]

                if not game.players.get(pid):
                    if player[J_SKIN] == SKIN_BLUE:
                        skin = res.textures.robot_blue
                    else:
                        skin = res.textures.robot_green

                    new_player = {pid: Robot(Point(0, 0), skin, angle=0)}
                    new_player[pid].texture.set_size(Size(30, 30))
                    game.players.update(new_player)

                game.players[pid].position = Point(player[J_POSITION_X], player[J_POSITION_Y])
                game.players[pid].texture.set_angle(player[J_ANGLE])
        elif command == ID:
            client.id = data[1]

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print("Socket closed, stop the event loop")
        loop = asyncio.get_event_loop()
        loop.stop()


if __name__ == "__main__":
    pygame.init()

    asyncio_loop = asyncio.get_event_loop()

    client = Client()

    res = Resources(sounds_volume=0.5)

    main_form = Core("GORA alpha 0.2", Size(FORM_WIDTH, FORM_HEIGHT), res.background, FPS * 1)
    game = Game(res)
    main_form.add_object(game)

    udp_loop = asyncio.new_event_loop()
    connect = asyncio_loop.create_datagram_endpoint(
        lambda: EchoClientProtocol(asyncio_loop),
        remote_addr=('127.0.0.1', 22000))
    transport, protocol = asyncio_loop.run_until_complete(connect)
    asyncio_loop.run_until_complete(main(transport))
