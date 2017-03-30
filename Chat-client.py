import socket
import threading
import sys
import re
import json


class Client:
    def __init__(self, host, name=None, portPP=6000):
        self._name = name
        self._host = host
        self._port = 5000
        self._socketS = socket.socket()
        self._socketPP = socket.socket(type=socket.SOCK_DGRAM)
        self._socketPP.bind((socket.gethostname(), portPP))
        self._clients = {}
        self._running = True

    def _send(self, txt):
        msg = txt.encode()
        totalsent = 0
        while totalsent < len(msg):
            sent = self._socketS.send(msg[totalsent:])
            totalsent += sent

    def refreshClients(self, msg):
        clients_co = json.loads(msg)
        for elem in clients_co:
            self._clients[elem] = tuple(clients_co[elem])
        print(self._clients)

    def treat(self, order, msg):
        orders = {
            '#senda': print,
            '#clients': self.refreshClients
        }
        if order in orders:
            orders[order](msg)

    def _listen(self):
        while self._running:
            try:
                data = self._socketS.recv(4096).decode()
                order, msg = self.analyse(data)
                self.treat(order, msg)
            except:
                pass

    def _listenPP(self):
        while self._running:
            try:
                data, cl = self._socketPP.recvfrom(4096)
                msg = 'MP ' + str(data.decode())
                print(msg)
            except:
                pass

    def analyse(self, txt):
        pattern = r'(?P<order>#[a-z]*) *(?P<message>.*)'
        p = re.compile(pattern)
        m = p.match(txt)
        if m is not None:
            order = m.group('order')
            msg = m.group('message')
            return order, msg
        else:
            txt = 'Error, you send a wrong message ' + str(self._name)
            return '#client', txt

    def sendToAll(self, txt):
        msg = '#senda ' + txt
        self._send(msg)

    def requestConnected(self):
        msg = '#clients'
        self._send(msg)

    def chooseName(self, dico):     # no space in the name ??
        print("You can't choose a name from this list :")
        print(dico['name forbidden'])
        ok = False
        while ok is not True:
            name = str(input("You're name:"))
            if name not in dico['name forbidden']:
                ok = True
                return(name)
            else:
                print('choose a other name please')
                ok = False

    def privatemsg(self, param):    # mp ne supporte les noms avec un espace
        dest, msg = param.split(' ', 1)
        if dest in self._clients:
            try:
                self._socketPP.sendto(msg.encode(), self._clients[dest])
            except Exception as e:
                print(e)
                print('mp failed')
        else:
            print('Wrong name')

    def run(self):
        handlers = {
            '/exit': self._exit,
            '/send': self.sendToAll,
            '/clients': self.requestConnected,
            '/mp': self.privatemsg
        }
        self._socketS.connect((self._host, self._port))
        self._name = self.chooseName(json.loads(self._socketS.recv(2048).decode()))
        self._send(self._name)
        self._send(str(self._socketPP.getsockname()[0]))
        self._send(str(self._socketPP.getsockname()[1]))
        threading.Thread(target=self._listen).start()
        threading.Thread(target=self._listenPP).start()
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
            else:
                print("Command not recognize")

    def _exit(self):
        print('Goodbye', self._name)
        self._running = False
        self._socketPP.shutdown(socket.SHUT_RDWR)
        self._socketPP.close()
        self._socketS.shutdown(socket.SHUT_RDWR)
        self._socketS.close()

if __name__ == "__main__":
    h = str(input('address to connect:',))
    ppp = int(input('n° port pp:',))
    Client(host=h, portPP=ppp).run()
