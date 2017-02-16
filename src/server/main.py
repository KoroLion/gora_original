# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import socketserver
import pickle
import threading
import time
from classes.helper_types import Position

PORT = 22000


class Dot:
    def __init__(self, position):
        self.position = position

player1 = Dot(Position(1, 1))


class TCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        data = pickle.loads(self.request.recv(1024))
        cur_thread = threading.current_thread()
        print("{} wrote: {}".format(self.client_address[0], data))
        # just send back the same data, but upper-cased
        if data == 'get_data':
            self.request.sendall(pickle.dumps(player1, 2))


server = socketserver.ThreadingTCPServer(('', PORT), TCPHandler)
ip, port = server.server_address
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()


def main():
    while True:
        time.sleep(1)
        player1.position.x += 1
        player1.position.y += 2
        print(player1.position.x)

    server.shutdown()
    server.server_close()

if __name__ == "__main__":
    main()
