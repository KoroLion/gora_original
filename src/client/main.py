# -*- coding: utf-8 -*-
import socket
import pickle
import threading
from classes.helper_types import Position, Size
from classes.game_object import GameObject
from classes.core import Core
from classes.constants import *
from classes.resources import Resources
from classes.game import Game
from time import sleep
import pygame

PORT = 22000


class Dot(object):
    def __init__(self, position):
        self.position = position

pygame.init()

res = Resources(sounds_volume=0.5)

form = Core("MSHP Pacman", Size(FORM_WIDTH, FORM_HEIGHT),
            res.background, FPS * 1)
game = Game(res)
form.add_object(game)


def display():
    while True:
        #threading.Lock().acquire()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', PORT))
        sock.sendall(pickle.dumps('get_data', 2))

        data = sock.recv(1024)
        if data:
            data = pickle.loads(data)
            game.player.position = data.position
            print('{}:{}'.format(data.position.x, data.position.y))

        sock.close()
        #threading.Lock().release()
        sleep(1)


display_thread = threading.Thread(target=display)
display_thread.daemon = True
display_thread.start()


def main():
    while not form.terminated:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                form.terminate()

        res.update()
        game.update()
        form.update()

if __name__ == "__main__":
    main()
