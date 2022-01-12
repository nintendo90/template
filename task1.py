import socket
import argparse
import pickle
import sys

HEADERSIZE = 10
HOST = socket.gethostname()
PORT = 60002

def send_msg(sock, msg):
    msg = f"{len(msg):<{HEADERSIZE}}" + msg
    sock.sendall(bytes(msg, 'utf-8'))

def recv_msg(sock):
    full_msg = ''
    new_message = True

    while True:
        msg = sock.recv(HEADERSIZE + 1)
        if new_message:
            msglen = int(msg[:HEADERSIZE])
            new_message = False
        full_msg += msg.decode("utf-8")
        if len(full_msg) - HEADERSIZE == msglen:
            new_message = True
            return full_msg[HEADERSIZE:]


def send_obj(sock, obj):
    d = pickle.dumps(obj)
    header = bytes(f"{len(d):<{HEADERSIZE}}", 'utf-8')
    sock.sendall(header+d)

def recv_obj(sock):
    full_msg = b''
    new_message = True

    while True:
        msg = sock.recv(HEADERSIZE + 1)
        if new_message:
            msglen = int(msg[:HEADERSIZE].decode('utf-8'))
            new_message = False
        full_msg += msg
        if len(full_msg) - HEADERSIZE == msglen:
            new_message = True
            return pickle.loads(full_msg[HEADERSIZE:])


def server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((host, port))
    sock.listen(5)

    tasks = []
    is_session = False

    while True:
        clientsock, address = sock.accept()
        print(f"Connection established from {address}!")

        while True:
            msg = recv_msg(clientsock)
            if msg == "start_list_session;":
                is_session = True
                print("Starting session...")
            elif msg == "end_list_session;":
                is_session = False
                print("Ending session...")
                clientsock.close()
                sock.close()
                sys.exit(0)
            elif msg == "show_list;":
                send_obj(clientsock, tasks)
            elif is_session:
                tasks.append(msg)
            else:
                pass




def client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((host, port))

    while True:
        msg = input("$")
        send_msg(sock, msg)
        if msg == "show_list;":
            my_tasks = recv_obj(sock)
            my_tasks = sorted(my_tasks)
            for task in my_tasks:
                print(task)

        elif msg == "end_list_session;":
            sock.close()
            sys.exit(0)
        




if __name__ == "__main__":
    choices = {"client": client, "server": server}
    parser = argparse.ArgumentParser(description="Simple tcp app")
    parser.add_argument("role", choices=choices, help="Role of the application")

    args = parser.parse_args()

    function = choices[args.role]
    function(HOST, PORT)