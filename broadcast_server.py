import socket
import threading
import sys

group_members = [("127.0.0.1", 8998), ("127.0.0.1", 8999), ("127.0.0.1", 9000)]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clients = []
id = 0


def broadcast(msg):
    for client in clients:
        client.send(msg)
    for i in range(len(group_members)):
        if(i!=id):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(group_members[i])
                s.send(msg)
                s.close()
            except:
                print("couldn't connect to ",group_members[i])
                continue

def handle(client):
    while True:
        try:
            msg = client.recv(1024)
            broadcast(msg)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            break


def receive():
    while True:
        client, address = server.accept()
        # print("Connected with {}".format(str(address)))
        print("Received a message...")
        clients.append(client)
        ack = {'message':'connected to server', 'clock':12, 'sender_id':id, 'ack':False, 'first':True}
        ack = (str)(ack)
        client.send(ack.encode())
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


id = int(sys.argv[1])
server.bind(group_members[int(id)])
server.listen(5)

receive()