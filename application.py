import argparse
import socket
import sys
import select

HEADERSIZE = 10
HOST = socket.gethostname()
PORT = 60001


def recv_msg(sock):
    full_msg = ''
    new_msg = True

    while True:
        msg = sock.recv(HEADERSIZE + 1)

        if new_msg:
            msglen = int(msg[:HEADERSIZE].decode('utf-8'))
            new_msg = False
        full_msg += msg.decode("utf-8")

        if len(full_msg) - HEADERSIZE == msglen:
            new_msg = True
            return full_msg[HEADERSIZE:]

def send_msg(sock, msg):
    msg = f"{len(msg):<{HEADERSIZE}}" + msg
    sock.sendall(bytes(msg, "utf-8"))


def server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((host, port))
    sock.listen(5)

    while True:
        clientsock, address = sock.accept()
        print(f"Connection established from {address}!")

        send_msg(clientsock, "Welcome to the server!")

        while True:
            sockets_list = [sys.stdin, clientsock]
            read_sockets, write_socket, error_socket = select.select(sockets_list,[],[])

            for s in read_sockets:
                if s == clientsock:
                    msg = recv_msg(s)
                    print(msg)
                else:
                    msg = sys.stdin.readline()
                    send_msg(clientsock, msg)


def client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.connect((host, port))

    msg = recv_msg(sock)
    print(msg)

    while True:
        sockets_list = [sys.stdin, sock]
        read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])

        for s in read_sockets:
            if s == sock:
                msg = recv_msg(s)
                print(msg)
            else:
                msg = sys.stdin.readline()
                send_msg(sock, msg)



if __name__ == '__main__':
    choices = {'client': client, 'server': server}
    arguments = argparse.ArgumentParser(description="Simple TCP server client application")
    arguments.add_argument("role", choices=choices, help="Role of the app")

    args = arguments.parse_args()

    function = choices[args.role]
    function(HOST,PORT)