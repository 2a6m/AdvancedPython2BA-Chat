import socket
import threading

class Client():
    def __init__(self, host, name):
        self._name = name
        self._host = host
        self._port = 5000
        self._socket = socket.socket()
        self._running = True

    def send_msg(self, txt):
        msg = self._name + " - " + txt
        msg = msg.encode()
        totalsent = 0
        while totalsent < len(msg):
            sent = self._socket.send(msg[totalsent:])
            totalsent += sent

    def listen(self):
        while self._running:
            data = self._socket.recv(4096).decode()
            if len(data) != 0:
                print('Reçu', len(data), 'octets :')
                print(data)

    def run(self):
        self._socket.connect((self._host, self._port))
        threading.Thread(target=self.listen).start()
        while self._running:
            ask = input()
            if ask == 'Q':
                self._running = False
            else:
                self.send_msg(ask)
        self._socket.close()
        quit()

if __name__ == "__main__":
    h = str(input('address to connect:',))
    n = str(input("You're name:"))
    Client(host=h, name=n).run()

