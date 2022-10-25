from __future__ import annotations
import logging
import socket
import pickle
import time
from typing import TYPE_CHECKING
from .base_logger import init_logger

if TYPE_CHECKING:
    from .game import OnlineGameInfo


class Network:
    """Acts as a socket connection to the server for multiplayer games."""
    def __init__(self, game_info: OnlineGameInfo) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = 'localhost'
        self.port = 5555
        self.addr = (self.server, self.port)
        self.game_info = game_info
        self.connect()

    def connect(self):
        self.client.connect(self.addr)
        self.data = self.send_data(self.game_info)

    def send_data(self, data):
        self.client.send(pickle.dumps(data))
        return pickle.loads(self.client.recv(2048))
    
    def disconnect(self):
        try:
            self.send_data('disconnect')
        except Exception:
            pass
        time.sleep(0.5) # Wait for the server to respond to the disconnect

        # Ideally, the server would have closed the conection for us,
        # but just in case it didn't, we manually leave below
        try:
            self.client.close()
        except Exception:
            pass

    def restart(self):
        init_logger()
        logging.info('Restarting connection...')
        self.disconnect()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()


def check_internet(host="8.8.8.8", port=53, timeout=3):
    """
    Checks whether internet connection is available
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    https://stackoverflow.com/a/33117579
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False