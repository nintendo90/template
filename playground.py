import socket
import argparse

ip = '127.0.0.1'
port = 12345

def server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip, port))
    sock.listen(1)
    print(f"listening at {sock.getsockname()}")
    while True:
        conn, addr= sock.accept()
        print(f"Connection from {addr} has been established.")
        conn.send(bytes("Hello my name is murad", "utf-8"))
        conn.close()
        break

def client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    full_msg = ''
    while True:
        message = sock.recv(8).decode('utf-8')
        full_msg += message
        if len(message) <= 0:
            sock.close()
            break

    print(full_msg)

if __name__ == "__main__":
    choices = {'client': client, 'server': server}
    parser = argparse.ArgumentParser(description='Send and receive over TCP')
    parser.add_argument('role', choices=choices, help='which role play server or client')
    args = parser.parse_args()
    function = choices[args.role]
    function()
