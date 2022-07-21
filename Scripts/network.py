import socket
import pickle

class Network:
    def __init__(self) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = '192.168.2.13'
        self.port = 5555
        self.addr = (self.server, self.port)
        self.data = self.conect()
    
    def conect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048))
        except Exception as e:
            print(e)
    
    def send_data(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)


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