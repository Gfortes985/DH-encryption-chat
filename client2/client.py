import socket
import random
import sys
import _thread

pub_key = None
prv_key = None

name = input("ENTER NAME >> ")

try:
    with open("pub.key","r") as f:
        key = f.read()
        if key == None:
            raise Exception
        else:
            pub_key = int(key)
except:
    with open("pub.key","w") as f:
        pub_key = random.randint(5000,50000)
        f.write(str(pub_key))

try:
    with open("prv.key","r") as f:
        key = f.read()
        if f.read() == None:
            raise Exception
        else:
            prv_key = int(key)
except:
    with open("prv.key","w") as f:
        prv_key = random.randint(5000,50000)
        f.write(str(prv_key))


sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(('localhost',4556))

laddr = sock.getsockname()


server_pub_key = int(sock.recv(1024))
sock.send(str(pub_key).encode())

partial_key = server_pub_key**prv_key%pub_key

server_partial_key = sock.recv(1024).decode()

if server_partial_key == "exit":
    sys.stdout.write("YOUR PUBLIC KEY NOT ALLOWED")
    exit(0)
else:
    server_partial_key = int(server_partial_key)

sock.send(str(partial_key).encode())
full_key = server_partial_key**prv_key%pub_key
port = (sock.recv(1024).decode())
sys.stdout.write(f"CONNECTION ESTABLISHED ON PORT {port}\n")
port = int(port)
sock.shutdown(socket.SHUT_RDWR)
sock.close()
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(("localhost",port))

raddr = sock.getpeername()

sys.stdout.write(f"PRIVATE KEY : {prv_key}\n")
sys.stdout.write(f"PUBLIC KEY : {pub_key}\n")
sys.stdout.write(f"LOCAL ADDRESS : {laddr[0]}:{laddr[1]+1}\n")
sys.stdout.write(f"REMOTE ADDRESS : {raddr[0]}:{raddr[1]}\n")

def listen():
    while True:
        orig_mess = ""

        message = sock.recv(4096*2).decode()
        try:
            for i in message:
                orig_mess+=chr(ord(i)-full_key)
            sys.stdout.write('\r' + ' ' * 50 + '\r')
            orig_mess = orig_mess.split(":")
            sys.stdout.write(f"{orig_mess[0]} : {orig_mess[1]}\n")
            sys.stdout.write(">")
            sys.stdout.flush()
        except ValueError:
            continue




def send():
    while True:
        for line in sys.stdin:
            sys.stdout.write(">")
            sys.stdout.flush()
            decline = ""
            for i in name+":"+line.rstrip():
                decline+=chr(ord(i)+full_key)
            sock.send(decline.encode())


sys.stdout.write(">")
sys.stdout.flush()
_thread.start_new_thread(listen,())
send()
