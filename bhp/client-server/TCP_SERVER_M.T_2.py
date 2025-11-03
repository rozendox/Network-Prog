import socket
import threading


# Função para lidar com a conexão de cada cliente
def handle_client(client_socket, client_address):
    print(f"[+] Nova conexão de {client_address}")
    try:
        while True:

            data = client_socket.recv(1024)
            if not data:
                # Se não receber dados, encerra a conexão
                break
            print(f"Recebido de {client_address}: {data.decode('utf-8')}")


            client_socket.sendall(b"Mensagem recebida")
    except ConnectionResetError:
        print(f"[!] Conexão perdida com {client_address}")
    finally:
        client_socket.close()
        print(f"[-] Conexão encerrada com {client_address}")


# Configurações do servidor
SERVER_HOST = "0.0.0.0"  # Escuta em todas as interfaces de rede
SERVER_PORT = 9999


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(5)
print(f"[*] Servidor ouvindo na porta {SERVER_PORT}")

try:
    while True:
        client_socket, client_address = server_socket.accept()
        client_handler = threading.Thread(
            target=handle_client, args=(client_socket, client_address)
        )
        client_handler.start()
except KeyboardInterrupt:
    print("\n[!] Servidor interrompido.")
finally:
    server_socket.close()
    print("[*] Servidor fechado.")
