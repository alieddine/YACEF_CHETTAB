import socket
from _thread import *
import sys

server = "192.168.1.33"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(3)
print("Waiting for a connection, Server Started")

def read_pos(str):
    str = str.split(",")
    return [float(str[0]), float(str[1]), float(str[2])]


def make_pos(tup):
    return str(tup[0]) + "," + str(tup[1]) + "," + str(tup[2])


pos = []


def threaded_client(conn, player):
    conn.send(str.encode(make_pos(pos[player])))
    reply = ""
    while True:
        try:
            reply = ""
            data = read_pos(conn.recv(2048).decode())
            pos[player] = data

            if not data:
                print("Disconnected")
                break
            else:
                if len(pos) == 1:
                    reply = "NO_PLAYERS"
                else:
                    for i in range(len(pos)):
                        if player != i:
                            if reply == "":
                                reply += make_pos(pos[i])
                            else:
                                reply += ":" + make_pos(pos[i])

                print("Received: ", data)
                print("Sending : ", reply)

            conn.sendall(str.encode(reply))
        except Exception as e:
            print(f"An exception occurred: {e}")

    print("Lost connection")
    conn.close()


currentPlayer = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    print(pos)
    start_new_thread(threaded_client, (conn, currentPlayer))
    print(pos)
    if len(pos) == 0:
        pos = [[0, 0, -10]]
    else:
        pos.append((pos[currentPlayer - 1][0] + 2, pos[currentPlayer - 1][1], pos[currentPlayer - 1][1] + 2))
    print(pos)

    currentPlayer += 1
