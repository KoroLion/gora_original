"""!
@file Клиент
@brief Главный файл клиента
"""

from concurrent.futures import ThreadPoolExecutor
from time import sleep, time
import hashlib
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

from classes.l_net import LNet

IP = '127.0.0.1'
LOGIN = 'KoroLion'
SKIN = SKIN_BLUE
TRACKING_CAMERA = True

CENTER_POS = Point(FORM_WIDTH / 2, FORM_HEIGHT / 2)

TOKEN = hashlib.md5(str(time()).encode() + LOGIN.encode()).hexdigest()


class Client(object):
    """!
    @brief Храним данные для взаимодействия потоков и базовые команды клиента
    """

    def __init__(self):
        self.commands = []
        self.angle = 0
        self.net = LNet(IP, PORT)

    def connect(self):
        self.net.connect()

        data = {J_COMMAND: CONNECT, J_TOKEN: TOKEN, J_LOGIN: LOGIN, J_SKIN: SKIN, J_ANGLE: 0}
        data = json.dumps(data)
        self.net.tcp_send(data)

    def send_commands(self):
        for command in self.commands:
            data = json.dumps({J_COMMAND: command, J_TOKEN: TOKEN})
            self.net.tcp_send(data)

        self.commands = []

    def get_data_from_server(self) -> str:
        data = {J_COMMAND: GET_DATA, J_TOKEN: TOKEN, J_ANGLE: self.angle}
        data = json.dumps(data)
        return self.net.tcp_send(data)

    def disconnect(self):
        data = json.dumps({J_COMMAND: DISCONNECT, J_TOKEN: TOKEN})
        self.net.tcp_send(data)
        self.net.disconnect()


def get_data(loop):
    """!
    @brief Поток получения информации о состоянии игры с сервера
    """

    client.connect()

    while not main_form.terminated and client.net.connected:
        if len(client.commands) > 0:
            client.send_commands()

        data = client.get_data_from_server()
        if data:
            players = json.loads(data)
            # players ~=
            # [{'2': '67bac7074979ff6707e44a0536ab468d', '10': 1, '11': 1},
            # {'2': '67bac7074979ff6707e44a0536ab468d', '10': 1, '11': 1}]

            # собираем токены сервера
            server_tokens = []
            for player in players:
                server_tokens.append(player[J_TOKEN])

            # собираем токены клиента
            client_tokens = []
            for token in game.players:
                client_tokens.append(token)

            # удаляем лишние объекты игроков на клиенте (которые отключились)
            for token in client_tokens:
                if not token in server_tokens:
                    game.players.pop(token)

            for player in players:
                # если нет объекта для игрока - создаём его (которые подключились)
                if not game.players.get(player[J_TOKEN]):
                    if player[J_SKIN] == SKIN_BLUE:
                        skin = res.textures.robot_blue
                    else:
                        skin = res.textures.robot_green

                    new_player = {player[J_TOKEN]: Robot(Point(0, 0), skin, angle=0)}
                    new_player[player[J_TOKEN]].texture.set_size(Size(30, 30))
                    game.players.update(new_player)

                # ставим игрока на новую позицию, полученную с сервера
                new_position = Point(player[J_POSITION_X], player[J_POSITION_Y])
                game.players[player[J_TOKEN]].position = new_position
                game.players[player[J_TOKEN]].texture.frame = rot_center(game.players[player[J_TOKEN]].start_image,
                                                                         player[J_ANGLE])

        sleep(0.02)


def rot_center(image: pygame.image, angle: float) -> pygame.image:
    """!
        @brief Поворачивает изображение с сохранением размеров
        @param image: картинка, которую надо перевернуть
        @param angle: градус поворота
        @return: повернутая картинка
    """
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


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


def main():
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
                    client.commands.append(C_GO_TOP_DOWN)
                if event.key == pygame.K_s:
                    client.commands.append(C_GO_BOTTOM_DOWN)
                if event.key == pygame.K_a:
                    client.commands.append(C_GO_LEFT_DOWN)
                if event.key == pygame.K_d:
                    client.commands.append(C_GO_RIGHT_DOWN)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    client.commands.append(C_GO_TOP_UP)
                if event.key == pygame.K_s:
                    client.commands.append(C_GO_BOTTOM_UP)
                if event.key == pygame.K_a:
                    client.commands.append(C_GO_LEFT_UP)
                if event.key == pygame.K_d:
                    client.commands.append(C_GO_RIGHT_UP)

        if game.players.get(TOKEN):
            mouse_pos = pygame.mouse.get_pos()
            if TRACKING_CAMERA:
                client.angle = get_angle(CENTER_POS, game.players[TOKEN].size,
                                         Point(mouse_pos[0], mouse_pos[1]))
            else:
                client.angle = get_angle(game.players.get(TOKEN).position, game.players[TOKEN].size,
                                         Point(mouse_pos[0], mouse_pos[1]))
            res.update()
            game.update()
            main_form.update(camera_mode=TRACKING_CAMERA, point=game.players.get(TOKEN).position)

    client.disconnect()

    # ждём, чтобы все соединение закрылись)
    sleep(0.5)
    asyncio_loop.stop()
    asyncio_loop.close()


if __name__ == "__main__":
    pygame.init()

    asyncio_loop = asyncio.get_event_loop()

    client = Client()

    res = Resources(sounds_volume=0.5)

    main_form = Core("GORA alpha 0.2", Size(FORM_WIDTH, FORM_HEIGHT), res.background, FPS * 1)
    game = Game(res)
    main_form.add_object(game)

    # превращаем курсор в прицел
    aim, mask = pygame.cursors.compile(res.aim, black='.', white='X', xor='o')
    pygame.mouse.set_cursor((24, 24), (0, 0), aim, mask)

    # создаём и запускаем поток, работающий с сетью
    print('Starting get_data thread...')
    executor = ThreadPoolExecutor(max_workers=1)
    asyncio_loop.run_in_executor(executor, get_data, asyncio_loop)

    main()
