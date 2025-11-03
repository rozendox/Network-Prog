import socket
import sqlite3
import json
import hashlib
import os
from cryptography.fernet import Fernet
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configuração do servidor UDP
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# Configuração do banco de dados SQLite
DB_NAME = "example.db"

# Chave de criptografia
KEY = Fernet.generate_key()
cipher = Fernet(KEY)


# Função para autenticar o cliente
def authenticate(client_key):
    # Verifique se a chave do cliente está correta
    if client_key != cipher.encrypt(b"secret_key").decode():
        return False
    return True


def create_table(table_name, columns):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = f"CREATE TABLE {table_name} ({', '.join(columns)})"
    cursor.execute(query)
    conn.commit()
    conn.close()


def drop_table(table_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = f"DROP TABLE {table_name}"
    cursor.execute(query)
    conn.commit()
    conn.close()


def alter_table(table_name, changes):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = f"ALTER TABLE {table_name} {changes}"
    cursor.execute(query)
    conn.commit()
    conn.close()


def list_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return [table[0] for table in tables]


def generate_pdf(table_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    data = cursor.fetchall()
    conn.close()

    c = canvas.Canvas("output.pdf", pagesize=letter)
    width, height = letter

    # Adicione código para gerar o PDF com os dados
    # Por exemplo, escrever os dados no PDF
    y = height - 50
    for row in data:
        c.drawString(100, y, str(row))
        y -= 20

    c.save()


def handle_request(data):
    try:
        data = json.loads(cipher.decrypt(data.encode()).decode())
        action, table_name = data.get("action"), data.get("table_name")
        if action == "create_table":
            columns = data.get("columns")
            create_table(table_name, columns)
        elif action == "drop_table python":
            return {"error": "Unknown action"}
        else:
            return {"error": "Unknown action"}
    except Exception as e:
        return {"error": str(e)}


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Servidor UDP escutando em {UDP_IP}:{UDP_PORT}")

while True:
    data, addr = sock.recvfrom(1024)
    client_key = data[:32].decode()  # Primeiros 32 bytes são a chave do cliente
    encrypted_request = data[32:]

    if authenticate(client_key):
        response = handle_request(encrypted_request)
        encrypted_response = cipher.encrypt(json.dumps(response).encode())
        sock.sendto(client_key.encode() + encrypted_response, addr)
    else:
        sock.sendto(b"Unauthorized", addr)
