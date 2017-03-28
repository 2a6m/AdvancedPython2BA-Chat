import socket
import threading


class Server():
    def __init__(self):
        self._host = ''
        self._port = 5000
        self._sock = socket.socket()
        self._sock.bind((self._host, self._port))
        self._clients = {}
        self._running = True

    def listen(self):
        self._sock.listen()
        print('listenning...')
        while self._running:
            client, addr = self._sock.accept()
            client.send("You're connected to the server".encode())
            name_client = client.recv(2048).decode()
            self._clients[client] = name_client
            threading.Thread(target=self.listenToClient, args=(client, addr)).start()

    def listenToClient(self, client, addr):
        while self._running:
            try:
                data = self._clients[client] + ' - ' + client.recv(2048).decode()
                print(addr, " : ", data)
                for cl in self._clients:
                    cl.send(data.encode())
            except:
                self._clients.pop(client)
                client.close()
                return False

if __name__ == "__main__":
    Server().listen()
    ask = str(input('[Q]uit'))
    if ask == 'Q':
        Server._running = False
        quit()
