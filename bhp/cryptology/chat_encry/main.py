import socket
import threading
import rsa


public_key, private_key = rsa.newkeys(1024)
public_partner = None



choice = input("do you want to host (1) or or connect (2)")

if choice == "1":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("192.168.0.141", 9998))
    server.listen()

    client, _ = server.accept()
    client.send(public_key.save_pkcs1("PEM"))
    public_partner = rsa.PublicKey.load_pkcs1(client.recv(1024))


elif choice == "2":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("192.168.0.141", 9998))
    public_partner = rsa.PublicKey.load_pkcs1(client.recv(1024))
    client.send(public_key.save_pkcs1("PEM"))
else:
    exit()


def sending_messages(c):
    while True:
        message = input("")
        #  USE THIS LOGIC TO ENCRY
        #  c.send(rsa.encrypt(message.encode(), public_partner))
        c.send(message.encode())
        print("You: " + message)


def receiving_messages(c):
    while True:
        #  USE THIS LOGIC TO ENCRY
        #  print("Partner:" + rsa.decrypt(c.recv(1024), private_key).decode())
        print("Partner:" + c.recv(1024).decode())


threading.Thread(target=sending_messages, args=(client,)).start()
threading.Thread(target=receiving_messages, args=(client,)).start()


