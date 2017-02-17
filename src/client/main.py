# -*- coding: utf-8 -*-
import socket
import threading
from time import sleep
import pickle
import pygame

from classes.constants import *
from classes.helper_types import Position, Size
from classes.resources import Resources
from classes.core import Core
from classes.game import Game
from classes.game_object import GameObject

PORT = 22000

GO_LEFT = 1
GO_RIGHT = 2
GO_TOP = 3
GO_BOTTOM = 4
GET_DATA = 5
DISCONNECT = 6


class CoreData(object):
    command = 0


class PlayerInfo(object):
    command = 0

    def __init__(self, position):
        self.position = position


class LNet(object):
    def __init__(self, ip, port, timeout):
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def tcp_send(self, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)  # Интернет, потокориентированный, TCP
        sock.connect((self.ip, self.port))
        sock.sendall(data)
        data = sock.recv(1024)
        sock.close()
        return data

    def udp_send(self, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # IPv4, датаграммный, UDP
        sock.connect((self.ip, self.port))
        sock.sendall(data)
        sock.close()

pygame.init()

res = Resources(sounds_volume=0.5)

form = Core("GORA pre-alpha 0.1", Size(FORM_WIDTH, FORM_HEIGHT),
            res.background, FPS * 1)
game = Game(res)
form.add_object(game)

net = LNet('localhost', PORT, 0.1)


def get_data():
    while not form.terminated:
        # threading.Lock().acquire() ?
        if CoreData.command != 0:
            net.udp_send(pickle.dumps(CoreData.command, 2))
            CoreData.command = 0

        data = net.tcp_send(pickle.dumps(GET_DATA, 2))
        if data:
            data = pickle.loads(data)
            game.player.position = data.position
            # print('{}:{}'.format(data.position.x, data.position.y))

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
                    CoreData.command = GO_TOP
                if event.key == pygame.K_s:
                    CoreData.command = GO_BOTTOM
                if event.key == pygame.K_a:
                    CoreData.command = GO_LEFT
                if event.key == pygame.K_d:
                    CoreData.command = GO_RIGHT

        res.update()
        game.update()
        form.update()
    net.udp_send(pickle.dumps(DISCONNECT, 2))


if __name__ == "__main__":
    main()
