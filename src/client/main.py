import threading
from time import sleep, time
import hashlib
import pygame
import json

from src.shared_constants import *
from src.helper_types import Size, Point

from classes.constants import FORM_WIDTH, FORM_HEIGHT, FPS
from classes.resources import Resources
from classes.core import Core
from classes.game import Game
from classes.game_object import GameObject

from classes.l_net import LNet

IP = '127.0.0.1'
LOGIN = 'KoroLion'

TOKEN = hashlib.md5(str(time()).encode() + LOGIN.encode()).hexdigest()


class Client(object):
    """!
    @brief Храним данные для взаимодействия потоков и базовые команды клиента
    """

    def __init__(self):
        self.command = 0
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
            net.udp_send(data.encode())
            self.command = 0
        except ConnectionError:
            self.connected = False

        return self.connected

    def get_data_from_server(self) -> str:
        data = {J_COMMAND: GET_DATA}
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
            # вид:
            # [{'2': '67bac7074979ff6707e44a0536ab468d', '10': 1, '11': 1},
            # {'2': '67bac7074979ff6707e44a0536ab468d', '10': 1, '11': 1}]

            for player in players:
                if not game.players.get(player[J_TOKEN]):
                    new_player = {player[J_TOKEN]: GameObject(Point(0, 0), res.textures.wall_type_default)}
                    game.players.update(new_player)

                new_position = Point(player[J_POSITION_X], player[J_POSITION_Y])
                game.players[player[J_TOKEN]].position = new_position

        sleep(0.05)


def main():
    """!
    @brief Поток отображения клиента
    """
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

    # создаём и запускаем поток, работающий с сетью
    get_data_thread = threading.Thread(target=get_data)
    get_data_thread.daemon = True
    get_data_thread.start()

    main()
