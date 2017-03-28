import socket
import threading
import sys
import re
import json

class Client():
    def __init__(self, host, name):
        self._name = name
        self._host = host
        self._port = 5000
        self._socket = socket.socket()

    def _send(self, txt):
        msg = txt.encode()
        totalsent = 0
        while totalsent < len(msg):
            sent = self._socket.send(msg[totalsent:])
            totalsent += sent

    def show(self, data):
        # print('Reçu', len(data), 'octets :')
        print(data)

    def refreshClients(self, msg):
        self._clients = json.dumps(msg)
        print(self._clients)

    def treat(self, order, msg):
        orders = {
            '/senda': self.show,
            '/clients': self.refreshClients
        }
        if order in orders:
            orders[order](msg)

    def _listen(self):  #quand on exit(), il attend encore un message avant de quitter
        while self._running:
            try:
                data = self._socket.recv(4096).decode()
            except:
                print('Error at the reception')
            order, msg = self.analyse(data)
            self.treat(order, msg)

    def analyse(self, txt):
        pattern = r'(?P<order>/[a-z]*) *(?P<message>.*)'
        p = re.compile(pattern)
        m = p.match(txt)
        if m is not None:
            order = m.group('order')
            msg = m.group('message')
            return order, msg
        else:
            return '/client', 'Error, you send a wrong message'

    def sendToAll(self, txt):
        msg = '/senda ' + txt
        self._send(msg)

    def requestConnected(self):
        msg = '/clients'
        self._send(msg)

    def run(self):
        handlers = {
            '/exit': self._exit,
            '/send': self.sendToAll,
            '/clients': self.requestConnected
        }
        self._running = True
        self._socket.connect((self._host, self._port))
        self._send(self._name)
        threading.Thread(target=self._listen).start()
        while self._running:
            line = sys.stdin.readline().rstrip() + ' '
            # Extract the command and the param
            command = line[:line.index(' ')]
            param = line[line.index(' ') + 1:].rstrip()
            # Call the command handler
            if command in handlers:
                try:
                    handlers[command]() if param == '' else handlers[command](param)
                except:
                    print("Erreur lors de l'exécution de la commande.")

    def _exit(self):    #erreur à cause du thread, il faut arrêter le thread
        self._running = False
        self._socket.close()

if __name__ == "__main__":
    h = str(input('address to connect:',))
    n = str(input("You're name:"))
    Client(host=h, name=n).run()

