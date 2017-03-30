import socket
import threading
import re
import json
import atexit


class Server:
    def __init__(self):
        self.__host = ''
        self.__port = 5000
        self.__sock = socket.socket()
        self.__sock.bind((self.__host, self.__port))
        self.__clients = {}
        self.__running = True
        self.__pattern = re.compile(r'(?P<order>#[a-z]*) *(?P<message>.*)')

    def _send(self, txt, client):
        msg = txt.encode()
        totalsent = 0
        while totalsent < len(msg):
            sent = client.send(msg[totalsent:])
            totalsent += sent

    def nameForbidden(self):
        lst = [self.__clients[cl] for cl in self.__clients]
        name_lst = [elem[0] for elem in lst] + ['']
        name = {'name forbidden': name_lst}
        return(json.dumps(name))

    def run(self):
        self.__sock.listen()
        print('listenning...')
        while self.__running:
            client, addr = self.__sock.accept()
            client.send(self.nameForbidden().encode())
            name_client = client.recv(2048).decode()
            pp_client = (client.recv(2048).decode(), int(client.recv(2048).decode()))
            self.__clients[client] = (name_client, addr, pp_client)
            print(self.__clients)
            client.send("#senda You're connected to the server".encode())
            threading.Thread(target=self.listenToClient, args=(client, addr)).start()

    def analyse(self, txt):
        m = self.__pattern.match(txt)
        if m is not None:
            order = m.group('order')
            msg = m.group('message')
            return order, msg
        else:
            return '#client', 'Error, you send a wrong message SERVER'

    def sendToExpeditor(self, **kwargs):
        msg = '#senda ' + kwargs['message']
        self._send(msg, kwargs['client'])

    def treat(self, order, msg, client, addr):
        orders = {
            '#senda': self.sendToAll,
            '#clients': self.sendClients,
            '#client': self.sendToExpeditor
        }
        if order in orders:
            orders[order](message=msg, client=client, address=addr)
        else:
            self.sendToExpeditor(message='You send a wrong message', client=client)

    def sendToAll(self, **kwargs):
        data = self.__clients[kwargs['client']][0] + ' - ' + kwargs['message']
        print(kwargs['address'], " : ", data)
        data = '#senda ' + data
        for cl in self.__clients:
            self._send(data, cl)

    def sendClients(self, **kwargs):
        data = {}
        for cl in self.__clients:
            data[str(self.__clients[cl][0])] = self.__clients[cl][2]
        print(data)
        data = json.dumps(data)
        txt = '#clients ' + data
        self._send(txt, kwargs['client'])

    def listenToClient(self, client, addr):
        while self.__running:
            try:
                txt = client.recv(2048).decode()
            except:
                self.__clients.pop(client)
                client.close()
                return False
            order, msg = self.analyse(txt)
            self.treat(order, msg, client, addr)

if __name__ == "__main__":
    Server().run()
