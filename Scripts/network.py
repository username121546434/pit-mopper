import logging
import socket
import pickle
import time
from .base_logger import init_logger


class Network:
    """Acts as a socket connection to the server for multiplayer games."""
    def __init__(self) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = '192.168.2.13'
        self.port = 5555
        self.addr = (self.server, self.port)
        self.data = self.connect()

    def connect(self):
        self.client.connect(self.addr)
        return pickle.loads(self.client.recv(2048))

    def send_data(self, data):
        self.client.send(pickle.dumps(data))
        return pickle.loads(self.client.recv(2048))
    
    def disconnect(self):
        self.send_data('disconnect')

    def restart(self):
        init_logger()
        logging.info('Restarting connection...')
        try:
            self.disconnect()
        except Exception:
            pass
        time.sleep(1) # Wait for the server to respond to the disconnect
        try:
            self.client.close()
        except Exception:
            pass
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data = self.connect()


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