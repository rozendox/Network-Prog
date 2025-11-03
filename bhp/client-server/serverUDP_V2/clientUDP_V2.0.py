import socket
import json
from cryptography.fernet import Fernet

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# Chave de criptografia
KEY = Fernet.generate_key()
cipher = Fernet(KEY)


def send_request(action, table_name, **kwargs):
    request = {
        "action": action,
        "table_name": table_name
    }
    if kwargs:
        request.update(kwargs)

    encrypted_request = cipher.encrypt(json.dumps(request).encode())
    client_key = cipher.encrypt(b"secret_key").decode()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(client_key.encode() + encrypted_request, (UDP_IP, UDP_PORT))

    data, addr = sock.recvfrom(1024)
    client_key_response = data[:32].decode()
    encrypted_response = data[32:]

    if client_key_response == "Unauthorized":
        print("Unauthorized access")
    else:
        response = json.loads(cipher.decrypt(encrypted_response).decode())
        print(response)


# Exemplo de uso
send_request("create_table", "users", columns="(id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
send_request("drop_table", "users")
send_request("alter_table", "users", changes="ADD COLUMN age INTEGER")
send_request("list_tables")
send_request("generate_pdf", "users")
