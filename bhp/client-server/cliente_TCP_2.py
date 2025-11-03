import socket
# Configurações do cliente
SERVER_HOST = "127.0.0.1"  # Endereço IP do servidor
SERVER_PORT = 9999         # Porta do servidor

# Criar o socket do cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print(f"[*] Conectado ao servidor {SERVER_HOST}:{SERVER_PORT}")


    mensagem = "Olá, servidor!"
    client_socket.sendall(mensagem.encode('utf-8'))
    resposta = client_socket.recv(1024)
    print(f"[*] Resposta do servidor: {resposta.decode('utf-8')}")

except ConnectionRefusedError:
    print("[!] Não foi possível conectar ao servidor.")
finally:
    # Encerrar a conexão com o servidor
    client_socket.close()
    print("[*] Conexão encerrada.")
