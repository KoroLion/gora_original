# -*- coding: utf-8 -*-
import socket
import pickle
from classes.helper_types import Position
from time import sleep

PORT = 22000


class Dot(object):
    def __init__(self, position):
        self.position = position


def main():
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', PORT))
        sock.sendall(pickle.dumps('get_data', 2))

        data = sock.recv(1024)
        if data:
            data = pickle.loads(data)
            print('{}:{}'.format(data.position.x, data.position.y))

        sleep(1)
        sock.close()

if __name__ == "__main__":
    main()
