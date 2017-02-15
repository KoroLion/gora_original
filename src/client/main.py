# -*- coding: utf-8 -*-
import socket

PORT = 22000


def main():
    sock = socket.socket()
    sock.connect(('localhost', PORT))
    sock.send('infit team!'.encode())

    data = sock.recv(1024)
    print(data)
    sock.close()

if __name__ == "__main__":
    main()