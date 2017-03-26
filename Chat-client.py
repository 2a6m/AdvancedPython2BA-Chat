import socket


def send_msg(s, smsg):
    msg = smsg.encode()
    totalsent = 0
    while totalsent < len(msg):
        sent = s.send(msg[totalsent:])
        totalsent += sent


def rcv_msg(s):
    data = s.recv(4096).decode()
    print('Reçu', len(data), 'octets :')
    print(data)


def run():
    rcv_msg(s)
    ask = input()
    if ask == 'Q':
        quit()
    else:
        send_msg(s, ask)
    run()

s = socket.socket()
ip = str(input('adresse IP:',))
port = int(input('n° port:',))
s.connect((ip, port))
run()
