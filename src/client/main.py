import threading
from time import sleep, time
import hashlib
import pygame
import math
import json

from src.shared_constants import *
from src.helper_types import Size, Point

from classes.constants import FORM_WIDTH, FORM_HEIGHT, FPS
from classes.resources import Resources
from classes.core import Core
from classes.game import Game
from classes.game_object import Robot

from classes.l_net import LNet

IP = '127.0.0.1'
LOGIN = 'KoroLion'
SKIN = SKIN_BLUE

TOKEN = hashlib.md5(str(time()).encode() + LOGIN.encode()).hexdigest()


class Client(object):
    """!
    @brief Храним данные для взаимодействия потоков и базовые команды клиента
    """

    def __init__(self):
        self.command = 0
        self.angle = 0
        self.connected = False

    def connect(self) -> bool:
        data = {J_COMMAND: CONNECT, J_TOKEN: TOKEN, J_LOGIN: LOGIN}
        data = json.dumps(data)
        try:
            net.tcp_send(data.encode())
            self.connected = True
        except ConnectionError:
            self.connected = False

        return self.connected

    def send_command(self) -> bool:
        data = json.dumps({J_COMMAND: self.command, J_TOKEN: TOKEN})
        try:
            net.tcp_send(data.encode())
            self.command = 0
        except ConnectionError:
            self.connected = False

        return self.connected

    def get_data_from_server(self) -> str:
        data = {J_COMMAND: GET_DATA, J_TOKEN: TOKEN, J_ANGLE: self.angle}
        data = json.dumps(data)
        try:
            return net.udp_send(data.encode())
        except ConnectionError:
            self.connected = False
            return ''

    def disconnect(self):
        try:
            data = json.dumps({J_COMMAND: DISCONNECT, J_TOKEN: TOKEN})
            net.udp_send(data.encode())
        except ConnectionError:
            pass

        self.connected = False


def get_data():
    """!
    @brief Поток получения информации о состоянии игры с сервера
    """
    while not client.connected:
        if not client.connect():
            pass
        #print('#ERROR: connection error')
        #sleep(1)

    while not main_form.terminated and client.connected:
        if client.command != 0:
            client.send_command()

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
                if not (token in server_tokens):
                    game.players.pop(token)

            for player in players:
                # если нет объекта для игрока - создаём его (которые подключились)
                if not game.players.get(player[J_TOKEN]):
                    new_player = {player[J_TOKEN]: Robot(Point(0, 0), res.textures.wall_type_default)}
                    game.players.update(new_player)

                # ставим игрока на новую позицию, полученную с сервера
                new_position = Point(player[J_POSITION_X], player[J_POSITION_Y])
                game.players[player[J_TOKEN]].position = new_position
                game.players[player[J_TOKEN]].angle = player[J_ANGLE]

        sleep(0.05)


def get_angle(pl_pos: Point, pos: list, size: Size) -> float:
    """!
    @brief Возращает угол между мышью и объектом

    @param size: Size(helper_types)
    @param pl_pos: list(координаты игрока)
    @param pos: list(координаты мыши)
    @return: float(градус поворота)
    """
    x = pos[0] + size.width - pl_pos.x
    y = pl_pos.y - pos[1] + size.height
    if x != 0:
        angle = math.atan(y / x) * 180 / 3.14
        if x > 0:
            angle += 270
            return angle
        else:
            angle += 90
            return angle
    else:
        angle = 0
        return angle


def main():
    """!
    @brief Поток отображения клиента
    """
    mouse_pos = (0, 0)
    while not main_form.terminated:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main_form.terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    client.command = GO_TOP
                if event.key == pygame.K_s:
                    client.command = GO_BOTTOM
                if event.key == pygame.K_a:
                    client.command = GO_LEFT
                if event.key == pygame.K_d:
                    client.command = GO_RIGHT
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos

        # game.players[TOKEN].angle = get_angle(game.players[TOKEN].position, mouse_pos, game.players[TOKEN].size)
        client.angle = get_angle(game.players[TOKEN].position, mouse_pos, game.players[TOKEN].size)

        res.update()
        game.update()
        main_form.update()

    if client.connected:
        client.disconnect()


if __name__ == "__main__":
    pygame.init()

    client = Client()

    res = Resources(sounds_volume=0.5)

    main_form = Core("GORA pre-alpha 0.1", Size(FORM_WIDTH, FORM_HEIGHT), res.background, FPS * 1)
    game = Game(res)
    main_form.add_object(game)

    net = LNet(IP, PORT)

    game.players.update({TOKEN: Robot(Point(0, 0), res.textures.wall_type_default, login=LOGIN)})

    # создаём и запускаем поток, работающий с сетью
    get_data_thread = threading.Thread(target=get_data)
    get_data_thread.daemon = True
    get_data_thread.start()

    main()
