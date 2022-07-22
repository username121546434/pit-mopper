"""Soon going to the server for online multiplayer pit mopper games.
Multiplayer games will most likely not coming anytime soon
"""
import socket
import threading
import sys
import traceback
from Scripts.game import OnlineGame
import pickle

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

games: dict[int, OnlineGame] = {}
id_count = 0

def new_client(conn: socket.socket, player: int, game_id: int):
    conn.send(pickle.dumps(player))

    while True:
        try:
            recieved = pickle.loads(conn.recv(2048))

            if recieved == 'disconnect':
                print('Client Disconnected')
                break
            elif isinstance(recieved, dict):
                games[game_id].update_info(player, recieved)

            print('Received: ', recieved)
            print('Sending: ', games[game_id])

            if player == 2 and not games[game_id].available:
                games[game_id].available = True

            conn.sendall(pickle.dumps(games[game_id]))
        except Exception:
            print(traceback.format_exc())
            print('Unknown error, disconnecting imeidietly')
            break

    print('Disconnecting...')
    if games[game_id].available:
        games[game_id].available = False
    else:
        try:
            games.pop(game_id)
        except KeyError:
            pass
    conn.close()


while True:
    conn, addr = s.accept()
    print('Connected to: ', addr)

    id_count += 1
    game_id = (id_count - 1)//2
    player = 1
    if id_count % 2 == 1:
        print('Creating new game...')
        game = OnlineGame(game_id)
        games[game_id] = game
    else:
        game = games[game_id]
        player = 2

    threading.Thread(target=new_client, args=(conn, player, game_id)).start()
