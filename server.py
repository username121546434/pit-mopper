"""
Soon going to the server for online multiplayer pit mopper games.
"""
from datetime import datetime
import os
import random
import socket
import threading
import sys
import traceback
from Scripts.game import OnlineGame, OnlineGameInfo
import pickle
import logging

if not os.path.exists('./logs'):
    os.mkdir('logs')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s | %(threadName)s]: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"./logs/log.log", encoding='utf-8')
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

games: dict[OnlineGameInfo, dict[int, OnlineGame]] = {}
player_count = 0

def new_client(conn: socket.socket):
    global player_count
    game_info = pickle.loads(conn.recv(2048))
    logging.info(f'{game_info = }')
    if game_info not in games:
        games[game_info] = {}

    logging.info('Looking for an available game...')
    game_id = None
    for game in games[game_info].values():
        if not game.available and not game.quit:
            game_id = game.id
            break

    if game_id is None:
        logging.info('No game found, generating new game id')
        game_id = random.randint(1000, 9999)
        while game_id in games[game_info].keys():
            game_id = random.randint(1000, 9999)

    if game_id not in games[game_info]:
        logging.info(f'Creating new game... {game_id = }')
        player = 1
        game = OnlineGame(game_id)
        games[game_info][game_id] = game
    else:
        logging.info(f'Existing game found, {game_id = }')
        game = games[game_info][game_id]
        player = 2

    logging.info(f'Sending player info... {player = }')
    conn.send(pickle.dumps(player))
    logging.info('Sent player info')
    while True:
        try:
            recieved = pickle.loads(conn.recv(2048))
            try:
                _ = games[game_info][game_id]
            except KeyError:
                conn.sendall(pickle.dumps('restart'))
                logging.info('Telling client to restart')

            if recieved == 'disconnect':
                logging.info('Client Disconnected')
                break
            elif isinstance(recieved, dict):
                games[game_info][game_id].update_info(player, recieved)
            elif isinstance(recieved, bool):
                if player == 1:
                    games[game_info][game_id].p1_finished = datetime.now()
                    games[game_info][game_id].p1_won = recieved
                else:
                    games[game_info][game_id].p2_finished = datetime.now()
                    games[game_info][game_id].p2_won = recieved

            logging.info(f'Received: {recieved}')
            logging.info(f'Sending: {games[game_info][game_id]}')

            if player == 2 and not games[game_info][game_id].available:
                games[game_info][game_id].available = True

            conn.sendall(pickle.dumps(games[game_info][game_id]))
        except Exception:
            logging.error(f'Unknown error, disconnecting imeidietly\n{traceback.format_exc()}')
            break

    logging.info('Disconnecting...')
    try:
        games[game_info][game_id].quit = True
        games[game_info].pop(game_id)
    except KeyError:
        logging.info('Failed to delete game as it was already deleted')
    else:
        logging.info('Deleted game')
    player_count -= 1
    conn.close()


while True:
    conn, addr = s.accept()
    logging.info(f'Connected to: {addr}')
    player_count += 1

    threading.Thread(target=new_client, args=[conn]).start()
