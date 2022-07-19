"""Soon going to the server for online multiplayer pit mopper games.
Multiplayer games will most likely not coming anytime soon
"""
import socket
from _thread import *
import sys
from game import OnlineGame

server = '192.168.2.13' # This may look like I mistakenly put my IP address here but its not
# This is local address which means that it can only be used in my WIFI network
# So you can't DDOS me or anything like that

port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    sys.stderr.write(e)
else:
    print('Socket binded successfully')


s.listen()
print('Waiting for connection...')

games:dict[int, OnlineGame] = {}
id_count = 0

def new_client(conn:socket.socket):
    reply = 'random reply'
    conn.send('Connected'.encode())
    while True:
        try:
            data = conn.recv(2048)
            recieved = data.decode('utf-8')
            
            if not data:
                print('Client Disconnected')
                break
            else:
                print('Received: ', recieved)
                print('Sending: ', reply)
            
            conn.sendall(reply.encode('utf-8'))

        except Exception as e:
            sys.stderr.write(e + '\nUnknown error with client, disconnecting immeidietly')
            break

    print('Disconnecting...')
    conn.close()


while True:
    conn, addr = s.accept()
    print('Connected to: ', addr)

    id_count += 1
    game_id = (id_count - 1)//2
    if id_count % 2 == 1:
        print('Creating new game...')
        game = None
        games[game_id] = game
    else:
        game = games[game_id]

    start_new_thread(new_client, (), {'conn':conn})
