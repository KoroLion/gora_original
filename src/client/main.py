# -*- coding: utf-8 -*-
import socket
import threading
from time import sleep
import pickle
import pygame

from classes.helper_types import Position, Size
from classes.game_object import GameObject
from classes.core import Core
from classes.constants import *
from classes.resources import Resources
from classes.game import Game

PORT = 22000

GO_LEFT = 1
GO_RIGHT = 2
GO_TOP = 3
GO_BOTTOM = 4
GET_DATA = 5


class Dot(object):
    command = 0

    def __init__(self, position):
        self.position = position

pygame.init()

res = Resources(sounds_volume=0.5)

form = Core("GORA pre-alpha 0.1", Size(FORM_WIDTH, FORM_HEIGHT),
            res.background, FPS * 1)
game = Game(res)
form.add_object(game)


def get_data():
    while True:
        # threading.Lock().acquire() ?
        if Dot.command != 0:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', PORT))
            sock.sendall(pickle.dumps(Dot.command, 2))
            sock.close()
            Dot.command = 0

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', PORT))
        sock.sendall(pickle.dumps(GET_DATA, 2))

        data = sock.recv(1024)
        if data:
            data = pickle.loads(data)
            game.player.position = data.position
            # print('{}:{}'.format(data.position.x, data.position.y))

        sock.close()
        # threading.Lock().release() ?
        sleep(0.05)


get_data_thread = threading.Thread(target=get_data)
get_data_thread.daemon = True
get_data_thread.start()


def main():
    while not form.terminated:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                form.terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    Dot.command = GO_TOP
                if event.key == pygame.K_s:
                    Dot.command = GO_BOTTOM
                if event.key == pygame.K_a:
                    Dot.command = GO_LEFT
                if event.key == pygame.K_d:
                    Dot.command = GO_RIGHT

        res.update()
        game.update()
        form.update()

if __name__ == "__main__":
    main()
