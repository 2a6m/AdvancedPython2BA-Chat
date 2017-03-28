import socket
import threading
import re
import json


class Server():
    def __init__(self):
        self._host = ''
        self._port = 5000
        self._sock = socket.socket()
        self._sock.bind((self._host, self._port))
        self._clients = {}
        self._running = True

    def _send(self, txt, client):
        msg = txt.encode()
        totalsent = 0
        while totalsent < len(msg):
            sent = client.send(msg[totalsent:])
            totalsent += sent

    def listen(self):
        self._sock.listen()
        print('listenning...')
        while self._running:
            client, addr = self._sock.accept()
            client.send("/senda You're connected to the server".encode())
            name_client = client.recv(2048).decode()
            self._clients[client] = (name_client, addr)
            threading.Thread(target=self.listenToClient, args=(client, addr)).start()

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

    def sendToExpeditor(self, txt, client, addr):
        msg = '/senda ' + txt
        self._send(client, msg)

    def treat(self, order, msg, client, addr):
        orders = {
            '/senda': self.sendToAll,
            '/clients': self.sendClients,
            '/client': self.sendToExpeditor
        }
        if order in orders:
            orders[order](msg, client, addr)
        else:
            self.sendToExpeditor('You send a wrong message', client, '')

    def sendToAll(self, msg, client, addr):
        data = self._clients[client][0] + ' - ' + msg
        print(addr, " : ", data)
        data = '/senda ' + data
        for cl in self._clients:
            self._send(data, cl)

    def sendClients(self, msg, client, addr):
        data = {}
        for cl in self._clients:
            data[str(self._clients[cl][0])] = self._clients[cl][1]
        print(data)
        data = json.dumps(data)
        txt = '/clients ' + data
        self._send(txt, client)

    def listenToClient(self, client, addr):
        while self._running:
            try:
                txt = client.recv(2048).decode()
            except:
                self._clients.pop(client)
                client.close()
                return False
            order, msg = self.analyse(txt)
            self.treat(order, msg, client, addr)

if __name__ == "__main__":
    Server().listen()
    ask = str(input('[Q]uit'))
    if ask == 'Q':
        Server._running = False
        quit()
