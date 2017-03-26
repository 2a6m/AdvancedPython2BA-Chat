import socket
import threading
import sys


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

    def _listen(self):  #quand on exit(), il attend encore un message avant de quitter
        while self._running:
            data = self._socket.recv(4096).decode()
            if len(data) != 0:
                #print('Reçu', len(data), 'octets :')
                print(data)

    def run(self):
        handlers = {
            '/exit': self._exit,
            '/send': self._send,
        }
        self._running = True
        self._socket.connect((self._host, self._port))
        print(type(self._name))
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

