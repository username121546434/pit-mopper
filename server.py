"""
Going to the server for online multiplayer pit mopper games.
"""
from datetime import datetime
import os
import random
import socket
import threading
import sys
import time
import traceback
from typing import Literal
from Scripts.game import OnlineGame, OnlineGameInfo
import pickle
import logging
from Scripts.constants import GAME_ID_MAX, GAME_ID_MIN

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
server = 'localhost'
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((server, port))

logging.info(f'Socket binded successfully to: {server}:{port}')

s.listen()
logging.info('Server started, waiting for connection...')

#              +-----------------------------------> The game info (with info: game size, mine count, and chording)
#              |             +---------------------> Mapping of game ID to a game
#              |             |    +----------------> The ID of the game
#              |             |    |      +---------> The game object that is shared between both clients
#              |             |    |      |
#              |             |    |      |
#              |             |    |      |
games: dict[OnlineGameInfo, dict[int, OnlineGame]] = {}
player_count = 0

def create_or_join_game(game_info: OnlineGameInfo) -> tuple[Literal[1, 2], int]:
    if game_info not in games:
        games[game_info] = {}

    logging.info('Looking for an available game...')
    game_id = None
    for game in games[game_info].values():
        if not game.is_full and not game.quit:
            game_id = game.id
            break

    if game_id is None:
        logging.info('No game found, generating new game id')
        game_id = random.randint(GAME_ID_MIN, GAME_ID_MAX)
        while game_id in games[game_info].keys():
            game_id = random.randint(GAME_ID_MIN, GAME_ID_MAX)

    if game_id not in games[game_info]:
        logging.info(f'Creating new game... {game_id = }')
        player = 1
        game = OnlineGame(game_id, game_info)
        games[game_info][game_id] = game
    else:
        logging.info(f'Existing game found, {game_id = }')
        game = games[game_info][game_id]
        player = 2
    return player, game_id


def join_game_from_id(conn: socket.socket, game_id: int) -> Literal[False] | tuple[Literal[2], OnlineGameInfo]:
    logging.info(f'Getting game from id...')
    game_info = get_game_from_id(game_id)
    if game_info is None: # Game does not exist
        logging.info('Game does not exist')
        conn.send(pickle.dumps(False))
        time.sleep(0.5) # Give the client time to respond
        return False
    else:
        if games[game_info][game_id].is_full: # Game is being played
            logging.info('Game is being played')
            conn.send(pickle.dumps(True))
            time.sleep(0.5) # Give the client time to respond
            return False
        return 2, game_info


def get_game_from_id(id_to_search: int, /):
    for game_info, value in games.items():
        for game_id, _ in value.items():
            if id_to_search == game_id:
                return game_info


def new_client(conn: socket.socket):
    global player_count

    game_info: OnlineGameInfo | int = pickle.loads(conn.recv(2048))
    logging.info(f'{game_info = }')
    if isinstance(game_info, OnlineGameInfo): # client wants to join any game with the same settings or create a new game
        player, game_id = create_or_join_game(game_info)
    else: # client wants to join a specific game using a game id
        game_id = game_info + 1 - 1
        x = join_game_from_id(conn, game_id)
        if x:
            player, game_info = x
        else:
            player_count -= 1
            return

    logging.info(f'Sending player info... {player = }')
    conn.send(pickle.dumps(player))
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

            print(f'Received: {recieved}')
            print(f'Sending: {games[game_info][game_id]}')

            if player == 2 and not games[game_info][game_id].is_full:
                games[game_info][game_id].is_full = True

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
    logging.info(f'Connected to new client')
    player_count += 1

    threading.Thread(target=new_client, args=[conn]).start()
