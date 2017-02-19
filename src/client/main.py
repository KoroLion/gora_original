# -*- coding: utf-8 -*-
import threading
from time import sleep, time
import hashlib
import pickle
import pygame

from classes.constants import FORM_WIDTH, FORM_HEIGHT, FPS
from classes.helper_types import Size
from classes.resources import Resources
from classes.core import Core
from classes.game import Game

from classes.l_net import LNet

IP = '127.0.0.1'
PORT = 22000
LOGIN = 'KoroLion'

TOKEN = hashlib.md5(str(time()).encode() + LOGIN.encode()).hexdigest()

GO_LEFT = 1
GO_RIGHT = 2
GO_TOP = 3
GO_BOTTOM = 4

CONNECT = 5
GET_DATA = 6
DISCONNECT = 7


class CoreData(object):
    """
    Храним данные для взаимодействия потоков
    """
    command = 0
    connected = False


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
        data = str(CONNECT) + ' ' + TOKEN + ' ' + LOGIN
        net.tcp_send(data.encode())
        CoreData.connected = True
    except ConnectionRefusedError:
        CoreData.connected = False
        print('Connection error!')

    while not main_form.terminated and CoreData.connected:
        # threading.Lock().acquire() ?
        if CoreData.command != 0:
            data = str(CoreData.command) + ' ' + TOKEN
            net.udp_send(data.encode())
            CoreData.command = 0

        data = net.tcp_send(str(GET_DATA).encode())
        if data:
            players = pickle.loads(data)
            game.player1.visible = False
            game.player2.visible = False
            game.player3.visible = False
            game.player4.visible = False
            n = 1
            for player in players:
                if n == 1:
                    game.player1.position = players[player].position
                    game.player1.visible = True
                elif n == 2:
                    game.player2.position = players[player].position
                    game.player2.visible = True
                elif n == 3:
                    game.player3.position = players[player].position
                    game.player3.visible = True
                elif n == 4:
                    game.player4.position = players[player].position
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
        data = str(DISCONNECT) + ' ' + TOKEN
        net.udp_send(data.encode())


if __name__ == "__main__":
    main()