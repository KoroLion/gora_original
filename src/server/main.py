import socket

PORT = 22000


def main():
    sock = socket.socket()
    sock.bind(('', PORT))
    sock.listen(1)
    conn, addr = sock.accept()
    print('Connected: {}'.format(addr))

    while True:
        data = conn.recv(1024)
        if not data:
            break
        conn.send(data.upper())

    conn.close()

if __name__ == "__main__":
    main()
