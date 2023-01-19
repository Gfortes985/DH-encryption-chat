import socket
import random
import _thread
import sys


pub_key = random.randint(5000,50000)
prv_key = random.randint(5000,50000)
full_keys = {}
clients = {}



sock_chat = socket.socket()
sock_chat.bind(("localhost",5555))

def key_send_loop():
    sock_enc = socket.socket()
    sock_enc.bind(("localhost", 4556))
    sock_enc.listen()
    while True:
        client, addr = sock_enc.accept()
        print(f"{addr[0]}:{addr[1]+1} CONNECTED")
        client.send(str(pub_key).encode())
        client_pub_key = int(client.recv(1024))
        allow_keys = []
        try:
            with open("allow.keys", "r") as f:
                text = f.read()
                if text == None:
                    print("FILL allow.keys FILE")
                    exit(0)
                text = text.split("\n")
                for i in text:
                    allow_keys.append(int(i))
        except:
            with open("allow.keys", "w") as f:
                print("FILL allow.keys FILE")
                exit(0)
        if client_pub_key in allow_keys:
            partial_key = pub_key ** prv_key % client_pub_key
            client.send(str(partial_key).encode())
            client_partial_key = int(client.recv(1024))
            full_key = client_partial_key ** prv_key % client_pub_key
            addr = (addr[0],addr[1]+1)
            full_keys[addr] = full_key
            client.send("5555".encode())
        else:
            client.send("exit".encode())

def sendall(client,orig_msg):
    for i in clients.keys():
        try:
            if clients[i] == client:
                continue
            clients[i].send(emsg(orig_msg, full_keys[i]).encode())
        except BrokenPipeError or KeyError:
            clients.pop(i, None)


def chat(client,addr):
    while True:
        try:
            message = client.recv(4096 * 2).decode()
        except ConnectionResetError:
            clients.pop(addr, None)
            sys.exit(0)

        orig_msg = dmsg(message,full_keys[addr])
        print(f"{addr[0]}:{addr[1]} - {message} -> {orig_msg}\n")
        print(clients.keys())
        sendall(client,orig_msg)

def chatloop():
    while True:
        sock_chat.listen()
        client, addr = sock_chat.accept()
        clients[addr] = client
        _thread.start_new_thread(chat,(client,addr))




def emsg(message, key):
    encmsg = ""
    for i in message:
        encmsg += chr(ord(i) + key)
    return encmsg

def dmsg(message,key):
    decmsg = ""
    for i in message:
        decmsg += chr(ord(i) - key)
    return decmsg



_thread.start_new_thread(key_send_loop,())
chatloop()







