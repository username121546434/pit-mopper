"""Soon going to the server for online multiplayer minesweeper games.
Multiplayer games will most likely not coming anytime soon
"""
import socket
from _thread import *

server = '192.168.2.13' # This may look like I mistakenly put my IP address here but its not
# This is local address which means that it can only be used in my WIFI network
# So you can't DDOS me or anything like that

port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(e)
else:
    print('Socket binded successfully')


s.listen()
print('Waiting for connection...')


def new_client(conn:socket.socket):
    reply = 'random reply'
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode('utf-8')
            
            if not data:
                print('Client Disconnected')
            else:
                print('Received: ', reply)
                print('Sending: ', reply)
            
            conn.sendall(reply.encode('utf-8'))

        except Exception as e:
            print(e)
            print('Unknown error with client, disconnecting immeidietly')
            break


while True:
    conn, addr = s.accept()
    print('Connected to: ', addr)

    start_new_thread(new_client, (conn))
