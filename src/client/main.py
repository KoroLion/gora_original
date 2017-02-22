# -*- coding: utf-8 -*-
import threading
from time import sleep, time
import hashlib
import pygame
import json

from src.shared_constants import *
from classes.constants import FORM_WIDTH, FORM_HEIGHT, FPS
from classes.helper_types import Size, Point
from classes.resources import Resources
from classes.core import Core
from classes.game import Game

from classes.l_net import LNet

IP = '127.0.0.1'
LOGIN = 'KoroLion'

TOKEN = hashlib.md5(str(time()).encode() + LOGIN.encode()).hexdigest()


class CoreData(object):
    """!
    @brief Храним данные для взаимодействия потоков и базовые команды клиента
    """
    command = 0
    connected = False

    def disconnect(self):
        pass


class PlayerInfo(object):
    """
    Класс информации об игроке, хранящейся на сервере
    """
    def __init__(self, position, speed):
        self.position = position
        self.speed = speed
        self.speed_amount = 3

    def update(self):
        self.position.x += self.speed.x
        self.position.y += self.speed.y

pygame.init()

res = Resources(sounds_volume=0.5)

main_form = Core("GORA pre-alpha 0.1", Size(FORM_WIDTH, FORM_HEIGHT), res.background, FPS * 1)
game = Game(res)
main_form.add_object(game)

net = LNet(IP, PORT, 0.1)


def get_data():
    """
    Поток получения информации о состоянии игры с сервера
    """
    try:
        data = {J_COMMAND: CONNECT, J_TOKEN: TOKEN, J_LOGIN: LOGIN}
        data = json.dumps(data)
        net.tcp_send(data.encode())
        CoreData.connected = True
    except ConnectionRefusedError:
        CoreData.connected = False
        print('Connection error!')

    while not main_form.terminated and CoreData.connected:
        # threading.Lock().acquire() ?
        if CoreData.command != 0:
            data = json.dumps({J_COMMAND: CoreData.command, J_TOKEN: TOKEN})
            net.udp_send(data.encode())
            CoreData.command = 0

        data = {J_COMMAND: GET_DATA}
        data = json.dumps(data)
        data = net.tcp_send(data.encode())
        if data:
            players = json.loads(data)
            # вид:
            # [{'2': '67bac7074979ff6707e44a0536ab468d', '10': 1, '11': 1},
            # {'2': '67bac7074979ff6707e44a0536ab468d', '10': 1, '11': 1}]

            game.player1.visible = False
            game.player2.visible = False
            game.player3.visible = False
            game.player4.visible = False
            n = 1
            for player in players:
                new_position = Point(player[J_POSITION_X], player[J_POSITION_Y])
                if n == 1:
                    game.player1.position = new_position
                    game.player1.visible = True
                elif n == 2:
                    game.player2.position = new_position
                    game.player2.visible = True
                elif n == 3:
                    game.player3.position = new_position
                    game.player3.visible = True
                elif n == 4:
                    game.player4.position = new_position
                    game.player4.visible = True
                n += 1
            # print('{}:{}'.format(data.position.x, data.position.y))

        # threading.Lock().release() ?
        sleep(0.05)


get_data_thread = threading.Thread(target=get_data)
get_data_thread.daemon = True
get_data_thread.start()


def main():
    """
    Поток отображения клиента
    """
    while not main_form.terminated:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main_form.terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    CoreData.command = GO_TOP
                if event.key == pygame.K_s:
                    CoreData.command = GO_BOTTOM
                if event.key == pygame.K_a:
                    CoreData.command = GO_LEFT
                if event.key == pygame.K_d:
                    CoreData.command = GO_RIGHT

        res.update()
        game.update()
        main_form.update()

    if CoreData.connected:
        data = json.dumps({J_COMMAND: DISCONNECT, J_TOKEN: TOKEN})
        net.udp_send(data.encode())


if __name__ == "__main__":
    main()
