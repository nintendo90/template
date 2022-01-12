import socket, argparse
import select
import sys

port=1060
host="127.0.0.1"

def server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(1)
    print('Listening at', sock.getsockname())
    while True:
        conn, addr = sock.accept()
        print('We have accepted a connection from', addr)
        todos = {}
        session=True
        while session:
            message = conn.recv(2048).decode('utf-8').strip()
            if not message.endswith(';'):
                conn.sendall('The command should end with semicolon(;)'.encode('utf-8'))
                continue
            if message == 'show_list;':
                for key in sorted(todos):
                    message = todos[key][0] + ' - ' + todos[key][1] + '\n'
                    conn.sendall(message.encode('utf-8'))
                    continue
            if message == 'end_list_session;':
                conn.close()
                session = False
                continue
            keywords = message.split('-')
            if len(keywords) == 2:
                tm = keywords[0].strip()
                time = int(tm.replace(':', ''))
                task = keywords[1].strip(' ;')
                todos[time] = [tm, task]
            else:
                conn.sendall('Not in correct format'.encode('utf-8'))


def client():
    mess = input()
    if mess.strip() != 'start_list_session;':
        print('Session should be started')
        print('The correct format: start_list_session;')
        print(mess.strip())
        sys.exit(0)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    while True:
        sockets_list = [sys.stdin, sock]
        read_sockets, write_sockets, error_sockets = select.select(sockets_list, [], [])
        for socks in read_sockets:
            if socks == sock:
                message = sock.recv(2048).decode('utf-8')
                print(message)
            else:
                command = input()
                sock.sendall(command.encode('utf-8'))
                if command == 'end_list_session;':
                    sock.close()
                    sys.exit()


if __name__ == "__main__":
    choices = {'server': server, 'client': client}
    parser = argparse.ArgumentParser(description="To do list")
    parser.add_argument("role", choices=choices, help="which role to play")
    args = parser.parse_args()
    function = choices[args.role]
    function()
