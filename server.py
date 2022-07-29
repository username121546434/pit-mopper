"""Soon going to the server for online multiplayer pit mopper games.
Multiplayer games will most likely not coming anytime soon
"""
import socket
import threading
import sys
import traceback
from Scripts.game import OnlineGame
import pickle
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s | %(threadName)s]: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    sys.last_type = exc_type
    sys.last_value = exc_value
    sys.last_traceback = exc_traceback
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception
server = '192.168.2.13' # This may look like I mistakenly put my IP address here but its not
# This is local address which means that it can only be used in my WIFI network
# So you can't DDOS me or anything like that

port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((server, port))

logging.info('Socket binded successfully')

s.listen()
logging.info('Server started, waiting for connection...')

games: dict[int, OnlineGame] = {}
id_count = 0

def new_client(conn: socket.socket, player: int, game_id: int):
    global id_count
    conn.send(pickle.dumps(player))
    while True:
        try:
            recieved = pickle.loads(conn.recv(2048))

            if recieved == 'disconnect':
                logging.info('Client Disconnected')
                break
            elif isinstance(recieved, dict):
                games[game_id].update_info(player, recieved)

            logging.info(f'Received: {recieved}')
            logging.info(f'Sending: {games[game_id]}')

            if player == 2 and not games[game_id].available:
                games[game_id].available = True

            conn.sendall(pickle.dumps(games[game_id]))
        except Exception:
            print(traceback.format_exc())
            logging.error('Unknown error, disconnecting imeidietly')
            break

    logging.info('Disconnecting...')
    if games[game_id].available:
        logging.info('Game no longer available')
        games[game_id].available = False
        id_count -= 1
    else:
        logging.info('Deleting game...')
        id_count -= 1
        games.pop(game_id)
    conn.close()


while True:
    conn, addr = s.accept()
    logging.info(f'Connected to: {addr}')

    id_count += 1
    game_id = (id_count - 1)//2
    player = 1
    if id_count % 2 == 1:
        logging.info('Creating new game...')
        game = OnlineGame(game_id)
        games[game_id] = game
    else:
        game = games[game_id]
        player = 2

    threading.Thread(target=new_client, args=(conn, player, game_id)).start()
