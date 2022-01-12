import socket, sys
from math import sqrt

host = "127.0.0.1"
port = 12345
commands = ['start_session;', 'add', 'distance', 'end_session;']

def server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))

    sock.listen(1)

    while True:
        sc, sockname = sock.accept()
        print(sockname, "joined")
        cities = {}
        while True:
            try:
                message = sc.recv(2048).decode('utf-8')
                parts = message.split()

                if parts[0] == commands[1]:
                    city = parts[1].strip(" 😊
                    x = float(parts[2].strip(" ,"))
                    y = float(parts[3].strip(" ;"))
                    cities[city] = [x, y]
                elif parts[0] == commands[2]:
                    city = parts[1].strip(" ;")
                    x, y = cities[city]
                    message = ""
                    for c in cities:
                        if c != city:
                            x2, y2 = cities[c]
                            distance = round(sqrt((x2-x)**2 + (y2-y)**2), 3)
                            message += f"\t{c}: {distance}\n"
                    
                    sc.send(message.encode('utf-8'))
                elif parts[0] == commands[3]:
                    print(sockname, "disconnected")
                    sc.close()
            except KeyboardInterrupt:
                sys.exit()
            except Exception:
                continue
    
def client():
    while True:
        inp = input("$").strip()
        if inp == commands[0]:
            break
        else:
            print('First, you need to start session by command "start_session;"')

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((host, port))

    while True:
        inp = input("$").strip()
        if not inp.endswith(";"):
            print('Commands must end with ";"')
            continue

        server.send(inp.encode('utf-8'))
        if inp == commands[3]:
            server.close()
            sys.exit()
        
        elif inp.startswith(commands[2]):
            message = server.recv(2048).decode('utf-8')
            print(message)

def main():
    roles = {'client': client, 'server': server}

    args = sys.argv

    if len(args) != 2:
        print("Command should be in form: python compute_distance {server|client}")
        sys.exit()

    if args[1] in roles:
        role = roles[args[1]]
        role()

if __name__ == "__main__":
    main()