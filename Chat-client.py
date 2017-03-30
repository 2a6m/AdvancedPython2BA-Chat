import socket
import threading
import sys
import re
import json


class Client:
    def __init__(self, host, name=None, portPP=6000):
        self.__name = name
        self.__hostS = host
        self.__portS = 5000
        self.__socketS = socket.socket()
        self.__socketPP = socket.socket(type=socket.SOCK_DGRAM)
        self.__socketPP.bind((socket.gethostname(), portPP))
        self.__clients = {}
        self.__running = True
        self.__pattern = re.compile(r'(?P<order>#[a-z]*) *(?P<message>.*)')

    def _send(self, txt):
        msg = txt.encode()
        totalsent = 0
        while totalsent < len(msg):
            sent = self.__socketS.send(msg[totalsent:])
            totalsent += sent

    def refreshClients(self, msg):
        clients_co = json.loads(msg)
        for elem in clients_co:
            self.__clients[elem] = tuple(clients_co[elem])
        print(self.__clients)

    def _listenS(self):
        while self.__running:
            try:
                data = self.__socketS.recv(4096).decode()
                order, msg = self.analyse(data)
                self.treat(order, msg)
            except:
                pass

    def _listenPP(self):
        while self.__running:
            try:
                data, cl = self.__socketPP.recvfrom(4096)
                msg = 'MP ' + str(data.decode())
                print(msg)
            except:
                pass

    def analyse(self, txt):
        m = self.__pattern.match(txt)
        if m is not None:
            order = m.group('order')
            msg = m.group('message')
            return order, msg
        else:
            txt = 'Error, you sent a wrong message ' + str(self.__name)
            return '#client', txt

    def treat(self, order, msg):
        orders = {
            '#senda': print,
            '#clients': self.refreshClients
        }
        if order in orders:
            orders[order](msg)

    def connection_server(self):
        self.__socketS.connect((self.__hostS, self.__portS))
        self.__name = self.chooseName(json.loads(self.__socketS.recv(2048).decode()))
        self._send(self.__name)
        self._send(str(self.__socketPP.getsockname()[0]))
        self._send(str(self.__socketPP.getsockname()[1]))
        threading.Thread(target=self._listenS).start()
        threading.Thread(target=self._listenPP).start()
        return

    def chooseName(self, dico):
        print("No space in the name")
        print("You can't choose a name from this list :")
        print(dico['Name forbidden'])
        ok = False
        while ok is not True:
            name = str(input("Your name:"))
            if name not in dico['Name forbidden'] and ' ' not in name:
                ok = True
                return (name)
            else:
                print('Choose another name')
                ok = False

    def run(self):
        handlers = {
            '/exit': self._exit,
            '/send': self.sendToAll,
            '/clients': self.requestConnected,
            '/mp': self.privatemsg
        }
        self.connection_server()
        while self.__running:
            line = sys.stdin.readline().rstrip() + ' '
            # Extract the command and the param
            command = line[:line.index(' ')]
            param = line[line.index(' ') + 1:].rstrip()
            # Call the command handler
            if command in handlers:
                try:
                    handlers[command]() if param == '' else handlers[command](param)
                except:
                    print("Error: couldn't execute the command")
            else:
                print("Invalid command")

    def sendToAll(self, txt):
        msg = '#senda ' + txt
        self._send(msg)

    def requestConnected(self):
        msg = '#clients'
        self._send(msg)

    def privatemsg(self, param):
        dest, msg = param.split(' ', 1)
        if dest in self.__clients:
            msg = self.__name + ' : ' + msg
            try:
                self.__socketPP.sendto(msg.encode(), self.__clients[dest])
            except Exception as e:
                print(e)
                print('mp failed')
        else:
            print('User not found')

    def _exit(self):
        print('Goodbye', self.__name)
        self.__running = False
        self.__socketPP.shutdown(socket.SHUT_RDWR)
        self.__socketPP.close()
        self.__socketS.shutdown(socket.SHUT_RDWR)
        self.__socketS.close()

if __name__ == "__main__":
    h = str(input('address to connect:',))
    ppp = int(input('n° port pp:',))
    Client(host=h, portPP=ppp).run()
